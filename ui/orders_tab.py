from __future__ import annotations

import csv
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from config import ORDER_STATES_COMMERCIAL, ORDER_STATES_PRODUCTION, ORDER_STATES_SHIPPING
from ui.dialogs.order_editor import OrderEditorDialog


class OrdersTab(ttk.Frame):
    def __init__(self, parent, *, order_service, client_service, product_service):
        super().__init__(parent)
        self.order_service = order_service
        self.client_service = client_service
        self.product_service = product_service
        self.selected_order_id: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        wrapper = ttk.Frame(self, padding=10)
        wrapper.pack(fill="both", expand=True)
        filters = ttk.Frame(wrapper)
        filters.pack(fill="x")

        ttk.Button(filters, text="Nova encomenda", style="Primary.TButton", command=self.create_order).pack(side="left")
        ttk.Label(filters, text="Pesquisar:").pack(side="left", padx=(10, 4))
        self.search_var = tk.StringVar()
        ttk.Entry(filters, textvariable=self.search_var, width=28).pack(side="left")

        ttk.Label(filters, text="Comercial:").pack(side="left", padx=(10, 4))
        self.comm_var = tk.StringVar(value="")
        ttk.Combobox(filters, textvariable=self.comm_var, values=[""] + ORDER_STATES_COMMERCIAL, width=16, state="readonly").pack(side="left")

        ttk.Label(filters, text="Produção:").pack(side="left", padx=(10, 4))
        self.prod_var = tk.StringVar(value="")
        ttk.Combobox(filters, textvariable=self.prod_var, values=[""] + ORDER_STATES_PRODUCTION, width=14, state="readonly").pack(side="left")

        ttk.Label(filters, text="Envio:").pack(side="left", padx=(10, 4))
        self.ship_var = tk.StringVar(value="")
        ttk.Combobox(filters, textvariable=self.ship_var, values=[""] + ORDER_STATES_SHIPPING, width=12, state="readonly").pack(side="left")

        ttk.Label(filters, text="Pago:").pack(side="left", padx=(10, 4))
        self.paid_var = tk.StringVar(value="")
        ttk.Combobox(filters, textvariable=self.paid_var, values=["", "Sim", "Não"], width=6, state="readonly").pack(side="left")

        ttk.Button(filters, text="Aplicar", command=self.refresh_data).pack(side="left", padx=(10, 0))

        body = ttk.Frame(wrapper)
        body.pack(fill="both", expand=True, pady=(10, 0))

        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(body, width=420)
        right.pack(side="right", fill="y", padx=(10, 0))

        cols = ("numero", "cliente_nome", "estado_comercial", "estado_producao", "estado_envio", "pago", "total", "created_at")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for c, w in (("numero", 140), ("cliente_nome", 240), ("estado_comercial", 120), ("estado_producao", 120), ("estado_envio", 110), ("pago", 60), ("total", 90), ("created_at", 160)):
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._on_select())

        ttk.Label(right, text="Detalhe da encomenda", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.detail_text = tk.Text(right, height=20, wrap="word")
        self.detail_text.pack(fill="both", expand=False, pady=(6, 0))

        ttk.Label(right, text="Itens", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.items_list = tk.Listbox(right, height=8)
        self.items_list.pack(fill="both", expand=False)

        actions = ttk.Frame(right)
        actions.pack(fill="x", pady=(10, 0))

        ttk.Button(actions, text="Editar", command=self.edit_selected).pack(fill="x", pady=2)
        ttk.Button(actions, text="Marcar paga", command=self.mark_paid).pack(fill="x", pady=2)
        ttk.Button(actions, text="Estados…", command=self.change_states).pack(fill="x", pady=2)
        ttk.Button(actions, text="Tracking…", command=self.update_tracking).pack(fill="x", pady=2)
        ttk.Button(actions, text="Exportar CSV", command=self.export_csv).pack(fill="x", pady=2)
        ttk.Button(actions, text="Duplicar", command=self.duplicate).pack(fill="x", pady=2)
        ttk.Button(actions, text="Cancelar", style="Danger.TButton", command=self.cancel).pack(fill="x", pady=2)

    def refresh_data(self) -> None:
        paid = None
        if self.paid_var.get() == "Sim":
            paid = 1
        elif self.paid_var.get() == "Não":
            paid = 0
        rows = self.order_service.list_orders(
            {
                "search": self.search_var.get(),
                "estado_comercial": self.comm_var.get() or None,
                "estado_producao": self.prod_var.get() or None,
                "estado_envio": self.ship_var.get() or None,
                "pago": paid,
            }
        )
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for r in rows:
            self.tree.insert("", "end", iid=r["id"], values=(r["numero"], r["cliente_nome"], r["estado_comercial"], r["estado_producao"], r["estado_envio"], "Sim" if r.get("pago") else "Não", f"{float(r.get('total') or 0):.2f}", r.get("created_at") or ""))

        self.selected_order_id = None
        self.detail_text.delete("1.0", tk.END)
        self.items_list.delete(0, tk.END)

    def _on_select(self) -> None:
        sel = self.tree.selection()
        if sel:
            self.selected_order_id = sel[0]
            self._load_detail(sel[0])

    def _load_detail(self, order_id: str) -> None:
        data = self.order_service.get_order_detail(order_id)
        o = data["order"]
        items = data["items"]
        lines = [
            f"Número: {o['numero']}",
            f"Cliente: {o.get('cliente_nome', '')}",
            f"Contacto: {o.get('cliente_telefone', '')} {o.get('cliente_email', '')}",
            f"Morada: {o.get('cliente_morada', '')}",
            f"Estados: {o['estado_comercial']} / {o['estado_producao']} / {o['estado_envio']}",
            f"Pago: {'Sim' if o.get('pago') else 'Não'}",
            f"Tracking: {o.get('tracking') or ''}",
            f"Prazo envio: {o.get('prazo_envio') or ''}",
            f"Notas: {o.get('notas') or ''}",
            "",
            f"Subtotal: {float(o.get('subtotal') or 0):.2f} €",
            f"Portes: {float(o.get('portes') or 0):.2f} €",
            f"Total: {float(o.get('total') or 0):.2f} €",
        ]
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, "\n".join(lines))
        self.items_list.delete(0, tk.END)
        for it in items:
            self.items_list.insert(tk.END, f"{it['sku']} | {it['nome']} | {it.get('tamanho') or ''} x{it['quantidade']} @ {float(it['preco_unit']):.2f}")

    def create_order(self):
        OrderEditorDialog(self, order_service=self.order_service, client_service=self.client_service, product_service=self.product_service, on_saved=self.refresh_data)

    def edit_selected(self):
        messagebox.showinfo("Info", "Edição completa em roadmap.")

    def mark_paid(self):
        if not self.selected_order_id:
            return messagebox.showinfo("Info", "Seleciona uma encomenda.")
        self.order_service.set_paid(self.selected_order_id, True)
        self.refresh_data()

    def change_states(self):
        oid = self.selected_order_id
        if not oid:
            return messagebox.showinfo("Info", "Seleciona uma encomenda.")
        data = self.order_service.get_order_detail(oid)
        o = data["order"]
        dlg = tk.Toplevel(self)
        dlg.title("Estados")
        comm = tk.StringVar(value=o["estado_comercial"])
        prod = tk.StringVar(value=o["estado_producao"])
        ship = tk.StringVar(value=o["estado_envio"])
        ttk.Combobox(dlg, textvariable=comm, values=ORDER_STATES_COMMERCIAL, state="readonly").pack(fill="x", padx=10, pady=5)
        ttk.Combobox(dlg, textvariable=prod, values=ORDER_STATES_PRODUCTION, state="readonly").pack(fill="x", padx=10, pady=5)
        ttk.Combobox(dlg, textvariable=ship, values=ORDER_STATES_SHIPPING, state="readonly").pack(fill="x", padx=10, pady=5)
        ttk.Button(dlg, text="Guardar", command=lambda: (self.order_service.update_states(oid, comm.get(), prod.get(), ship.get()), dlg.destroy(), self.refresh_data())).pack(fill="x", padx=10, pady=10)

    def update_tracking(self):
        if not self.selected_order_id:
            return messagebox.showinfo("Info", "Seleciona uma encomenda.")
        new = simpledialog.askstring("Tracking", "Código de tracking:", parent=self)
        if new is not None:
            self.order_service.update_tracking(self.selected_order_id, new)
            self.refresh_data()

    def export_csv(self):
        if not self.selected_order_id:
            return messagebox.showinfo("Info", "Seleciona uma encomenda.")
        data = self.order_service.get_order_detail(self.selected_order_id)
        o, items = data["order"], data["items"]
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"{o['numero']}.csv")
        if not path:
            return
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["numero", "cliente", "sku", "nome", "quantidade", "preco_unit"])
            for it in items:
                w.writerow([o["numero"], o.get("cliente_nome", ""), it.get("sku", ""), it.get("nome", ""), it.get("quantidade", 0), it.get("preco_unit", 0)])

    def duplicate(self):
        if not self.selected_order_id:
            return messagebox.showinfo("Info", "Seleciona uma encomenda.")
        self.order_service.duplicate_order(self.selected_order_id)
        self.refresh_data()

    def cancel(self):
        if not self.selected_order_id:
            return messagebox.showinfo("Info", "Seleciona uma encomenda.")
        if messagebox.askyesno("Confirmar", "Cancelar encomenda? (o stock devolvido é idempotente)"):
            self.order_service.cancel_order(self.selected_order_id)
            self.refresh_data()
