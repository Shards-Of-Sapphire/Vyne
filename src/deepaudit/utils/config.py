import os
from pathlib import Path
from dotenv import load_dotenv

# Automatically find the .env file in the project root
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_config(key, default=None):
    """Safely retrieve environment variables."""
    return os.getenv(key, default)

# Pre-defined helpers for DeepAudit
def is_debug():
    return get_config("DEBUG", "False").lower() == "true"

def get_pypi_token():
    return get_config("PYPI_TOKEN")