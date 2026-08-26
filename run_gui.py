"""Convenient development launcher: ``.venv/bin/python run_gui.py``."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from cult_mgmt.qt_gui import run  # noqa: E402


if __name__ == "__main__":
    run()
