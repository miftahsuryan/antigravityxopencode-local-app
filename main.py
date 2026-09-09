"""Root entrypoint untuk packaging / desktop launcher Flet."""

import flet as ft

from src.app.main import main

if __name__ == "__main__":
    ft.run(main)
