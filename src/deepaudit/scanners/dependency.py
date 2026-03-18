import requests

def verify_package(package_name):
    """Checks if a package exists on PyPI and returns its status."""
    # Standard libraries to ignore (os, sys, math, etc.)
    std_libs = ["os", "sys", "math", "re", "json", "time", "datetime", "random"]
    if package_name in std_libs:
        return True, "Standard Library"

    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            version = data['info']['version']
            return True, f"Verified (v{version})"
        elif response.status_code == 404:
            return False, "⚠️ HALLUCINATION: Package not found on PyPI!"
        else:
            return False, "Registry Timeout"
    except Exception:
        return False, "Connection Error"
