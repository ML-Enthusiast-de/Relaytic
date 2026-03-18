import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

for module_name in list(sys.modules):
    if module_name == "corr2surrogate" or module_name.startswith("corr2surrogate."):
        sys.modules.pop(module_name, None)
