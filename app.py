from __future__ import annotations

import tkinter as tk

import db
from config import APP_NAME
from services import build_services
from ui.main_window import MainWindow
from ui.theme import apply_brand_theme


def main() -> None:
    db.init_database()
    services = build_services()

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("1280x820")
    apply_brand_theme(root)
    MainWindow(root, services)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
