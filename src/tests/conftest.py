import sys
from pathlib import Path

# Allow `import src...` when running pytest from the repo root.
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))