# Engine's pyproject.toml declares a src/ layout that doesn't exist on
# disk, so `pip install -e .` is broken. Tests therefore import modules
# directly via sys.path — same way core/engine.py imports from core, etc.
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
  sys.path.insert(0, str(ENGINE_ROOT))
