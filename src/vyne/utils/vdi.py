import importlib.util
import importlib.metadata
import requests
from functools import lru_cache
from typing import Callable, Optional


@lru_cache(maxsize=512)
def _pypi_lookup(package: str, timeout: float = 3.0) -> Optional[dict]:
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def _pypi_lookup_result(package: str, timeout: float = 3.0) -> dict:
    """Return a registry result that distinguishes absence from unavailability."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return {"status": "verified", "data": resp.json()}
        if resp.status_code == 404:
            return {"status": "missing", "data": None}
        return {"status": "unavailable", "data": None}
    except Exception:
        return {"status": "unavailable", "data": None}


def _top_level_name(name: str) -> str:
    return name.split(".")[0]


def check_package(
    package: str,
    lookup: Optional[Callable[[str], dict]] = None,
) -> dict:
    """Perform a version-aware check for a package name.

    Returns a dict with keys:
      - installed: bool
      - installed_version: str|None
    - pypi_exists: bool|None (None means the registry could not be checked)
    - verification_status: verified|missing|unavailable
      - pypi_latest: str|None
      - semver_major_mismatch: bool
      - confidence: float  (higher -> more confident this is problematic)
    """
    result = {
        "package": package,
        "installed": False,
        "installed_version": None,
        "pypi_exists": None,
        "pypi_latest": None,
        "semver_major_mismatch": False,
        "confidence": 0.0,
        "verification_status": "unavailable",
    }

    name = _top_level_name(package)

    # Check local environment
    try:
        spec = importlib.util.find_spec(name)
        if spec is not None:
            result["installed"] = True
            try:
                result["installed_version"] = importlib.metadata.version(name)
            except Exception:
                result["installed_version"] = None
    except Exception:
        pass

    # Query PyPI for latest
    registry_result = (lookup or _pypi_lookup_result)(name)
    status = registry_result.get("status", "unavailable")
    pypi = registry_result.get("data")
    result["verification_status"] = status
    if status == "verified" and pypi:
        result["pypi_exists"] = True
        info = pypi.get("info", {})
        result["pypi_latest"] = info.get("version")
    elif status == "missing":
        result["pypi_exists"] = False

    # Simple semver-major mismatch heuristic
    try:
        if result["installed_version"] and result["pypi_latest"]:
            inst_major = str(result["installed_version"]).split(".")[0]
            latest_major = str(result["pypi_latest"]).split(".")[0]
            if inst_major != latest_major:
                result["semver_major_mismatch"] = True
    except Exception:
        pass

    # Heuristic confidence calculation
    # - If package not on PyPI -> likely hallucinated
    # - If not installed but on PyPI -> medium (could be omitted env)
    # - If installed and major mismatch -> medium-high
    if status == "missing":
        result["confidence"] = 0.95
    elif status == "verified" and not result["installed"]:
        result["confidence"] = 0.35
    elif status == "verified" and result["installed"] and result["semver_major_mismatch"]:
        result["confidence"] = 0.7
    elif status == "verified":
        result["confidence"] = 0.1

    return result


__all__ = ["check_package"]
