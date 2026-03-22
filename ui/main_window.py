from __future__ import annotations

from tkinter import ttk

from ui.orders_tab import OrdersTab


class MainWindow:
    def __init__(self, root, services: dict):
        self.root = root
        self.services = services
        self._build()

    def _build(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)

        self.orders_tab = OrdersTab(
            nb,
            order_service=self.services["order_service"],
            client_service=self.services["client_service"],
            product_service=self.services["product_service"],
        )
        nb.add(ttk.Frame(nb), text="Início")
        nb.add(self.orders_tab, text="Encomendas")
        nb.add(ttk.Frame(nb), text="Produtos")
        nb.add(ttk.Frame(nb), text="Clientes")
        nb.add(ttk.Frame(nb), text="Produção")
        nb.add(ttk.Frame(nb), text="Sistema")

        nb.bind("<<NotebookTabChanged>>", lambda _e: self.orders_tab.refresh_data())
