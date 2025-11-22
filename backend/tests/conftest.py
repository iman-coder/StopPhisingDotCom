import os
import sys
from pathlib import Path

# Ensure `backend` folder is on sys.path so `import app...` works
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

# Use a dedicated sqlite file for tests to avoid touching dev DB
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_db_for_tests.db")
