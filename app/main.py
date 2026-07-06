from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication

from app import __version__
from app.controller.app_controller import ApplicationController
from app.ui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="school-design-pipeline")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0

    app = QApplication(sys.argv)
    window = MainWindow(ApplicationController())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
