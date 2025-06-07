import sys
from pathlib import Path

# Ensure project src/ directory is on the Python path for tests
ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
if str(ROOT) not in sys.path:
    # Insert project root so ``import src`` works during tests
    sys.path.insert(0, str(ROOT))
    import importlib
    importlib.invalidate_caches()
