import importlib.util
import importlib.metadata
import requests
from functools import lru_cache
from typing import Optional


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


def _top_level_name(name: str) -> str:
    return name.split(".")[0]


def check_package(package: str) -> dict:
    """Perform a version-aware check for a package name.

    Returns a dict with keys:
      - installed: bool
      - installed_version: str|None
      - pypi_exists: bool
      - pypi_latest: str|None
      - semver_major_mismatch: bool
      - confidence: float  (higher -> more confident this is problematic)
    """
    result = {
        "package": package,
        "installed": False,
        "installed_version": None,
        "pypi_exists": False,
        "pypi_latest": None,
        "semver_major_mismatch": False,
        "confidence": 0.0,
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
    pypi = _pypi_lookup(name)
    if pypi:
        result["pypi_exists"] = True
        info = pypi.get("info", {})
        result["pypi_latest"] = info.get("version")

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
    if not result["pypi_exists"]:
        result["confidence"] = 0.95
    elif not result["installed"] and result["pypi_exists"]:
        result["confidence"] = 0.35
    elif result["installed"] and result["semver_major_mismatch"]:
        result["confidence"] = 0.7
    else:
        result["confidence"] = 0.1

    return result


__all__ = ["check_package"]
