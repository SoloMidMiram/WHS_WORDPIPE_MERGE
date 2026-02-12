import subprocess
import sys
from pathlib import Path

REQUIRED = ["python-docx", "rich"]

def ensure_installed():
    for pkg in REQUIRED:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"[Installer] Installing missing package: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def run_pipeline():
    from autobiography.cli import main
    main()

if __name__ == "__main__":
    ensure_installed()
    run_pipeline()
