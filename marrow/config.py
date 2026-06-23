import os
from pathlib import Path

# Paths
DEFAULT_DB_DIR = Path.home() / ".marrow"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "data.db"

# Load environment overrides
DB_PATH = Path(os.getenv("MARROW_DB_PATH", str(DEFAULT_DB_PATH)))
BACKEND_URL = os.getenv("MARROW_BACKEND_URL", "https://api.openai.com/v1").rstrip("/")
EXTRACT_MODEL = os.getenv("MARROW_EXTRACT_MODEL", "gpt-5.4-mini")

# Host / Port defaults
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7723

# Modes
MONITOR_ONLY = os.getenv("MARROW_MONITOR_ONLY", "0") == "1"
