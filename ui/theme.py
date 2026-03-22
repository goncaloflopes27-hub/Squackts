from __future__ import annotations

from tkinter import ttk

from config import BRAND_YELLOW


def apply_brand_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Primary.TButton", background=BRAND_YELLOW)
    style.configure("Danger.TButton", foreground="#FFFFFF", background="#EA4545")
