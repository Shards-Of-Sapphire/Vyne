import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_path="config.yaml"):
        self.path = Path(config_path)
        # 1. Standard Library Baseline (The "Safe" Python Modules)
        self.std_lib = {
            "sys", "os", "pathlib", "time", "json", "typing", 
            "logging", "abc", "math", "collections", "re"
        }
        self.data = self._load()
        # Load project-level .vynerc if present
        self.vyne_rc = self._load_vyne_rc()

    def _load(self):
        if not self.path.exists():
            return {"whitelist": [], "scanners": {}}
        with open(self.path, "r") as f:
            return yaml.safe_load(f)

    def get_trusted_namespaces(self):
        """
        Returns a unified set of:
        Internal Folders + Standard Lib + User config.yaml
        """
        internal = {"vyne", "src", "engine", "scanners", "utils"}
        user_defined = set(self.data.get("whitelist", []))
        
        # Combine everything into one master set
        return internal | self.std_lib | user_defined

    def _load_vyne_rc(self):
        """Load optional per-project .vynerc YAML file.

        Format example (.vynerc):
        ignore:
          - "ScannerNameToIgnore"
          - "some message substring to ignore"
        """
        rc_path = Path('.vynerc')
        if not rc_path.exists():
            return {"ignore": []}
        try:
            with open(rc_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                # Normalize
                return {"ignore": data.get("ignore", [])}
        except Exception:
            return {"ignore": []}

    def get_project_allowlist(self):
        """Return list of ignore patterns from .vynerc"""
        return list(self.vyne_rc.get("ignore", []))
    
# Automatically find the .env file in the project root
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_config(key, default=None):
    """Safely retrieve environment variables."""
    return os.getenv(key, default)

# Pre-defined helpers for Vyne
def is_debug():
    return str(get_config("DEBUG", "False")).lower() == "true"

def get_pypi_token():
    return get_config("PYPI_TOKEN")


__all__ = ["ConfigManager", "get_config", "is_debug", "get_pypi_token"]
