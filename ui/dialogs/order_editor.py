from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from config import ORDER_STATES_COMMERCIAL, ORDER_STATES_PRODUCTION, ORDER_STATES_SHIPPING


class OrderEditorDialog(tk.Toplevel):
    def __init__(self, parent, *, order_service, client_service, product_service, order_id=None, on_saved=None):
        super().__init__(parent)
        self.order_service = order_service
        self.client_service = client_service
        self.product_service = product_service
        self.order_id = order_id
        self.on_saved = on_saved
        self.title("Nova encomenda" if not order_id else "Editar encomenda")
        self.geometry("640x480")
        self.transient(parent)
        self.grab_set()
        self.items_buffer: list[dict] = []
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)
        self.client_var = tk.StringVar()
        self.portes_var = tk.StringVar(value="0")

        ttk.Label(frame, text="Cliente (ID)").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.client_var).pack(fill="x")
        ttk.Label(frame, text="Portes").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.portes_var).pack(fill="x")

        ttk.Button(frame, text="Guardar", style="Primary.TButton", command=self._save).pack(fill="x", pady=10)

    def _save(self):
        try:
            self.order_service.create_order(
                {
                    "client_id": self.client_var.get().strip(),
                    "estado_comercial": ORDER_STATES_COMMERCIAL[0],
                    "estado_producao": ORDER_STATES_PRODUCTION[0],
                    "estado_envio": ORDER_STATES_SHIPPING[0],
                    "portes": float(self.portes_var.get() or 0),
                    "items": self.items_buffer,
                }
            )
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)
