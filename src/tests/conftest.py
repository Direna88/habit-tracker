import sys
from pathlib import Path

# Add project root to PYTHONPATH so "src" can be imported in tests
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
