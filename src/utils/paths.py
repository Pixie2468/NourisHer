from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

DATA_DIR = ROOT / "data"

SRC_DIR = ROOT / "src"

if __name__ == "__main__":
    print(f"root: {ROOT}, data-dir: {DATA_DIR}")
