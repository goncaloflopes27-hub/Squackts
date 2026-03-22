from __future__ import annotations

import db


class DashboardService:
    def metrics(self) -> dict:
        with db.connect() as conn:
            total_orders = conn.execute("SELECT COUNT(*) AS n FROM orders").fetchone()["n"]
            open_orders = conn.execute(
                "SELECT COUNT(*) AS n FROM orders WHERE estado_comercial != 'cancelada' AND estado_envio != 'entregue'"
            ).fetchone()["n"]
            total_clients = conn.execute("SELECT COUNT(*) AS n FROM clients").fetchone()["n"]
            total_products = conn.execute("SELECT COUNT(*) AS n FROM products").fetchone()["n"]
            return {
                "total_orders": total_orders,
                "open_orders": open_orders,
                "total_clients": total_clients,
                "total_products": total_products,
            }
