from __future__ import annotations

from datetime import datetime

import db
from config import ORDER_STATES_COMMERCIAL, ORDER_STATES_PRODUCTION, ORDER_STATES_SHIPPING


class OrderService:
    def __init__(self, order_repo, product_repo, settings_repo, log_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.settings_repo = settings_repo
        self.log_repo = log_repo

    def list_orders(self, filters: dict):
        with db.connect() as conn:
            return [dict(r) for r in self.order_repo.list_orders(conn, filters)]

    def get_order_detail(self, order_id: str) -> dict:
        with db.connect() as conn:
            order = self.order_repo.get_order(conn, order_id)
            items = self.order_repo.get_items(conn, order_id)
            if not order:
                raise ValueError("Encomenda não encontrada")
            return {"order": dict(order), "items": [dict(i) for i in items]}

    def _next_order_number(self, conn) -> str:
        year = datetime.now().year
        key = f"order_seq_{year}"
        current = int(self.settings_repo.get(conn, key) or "0") + 1
        self.settings_repo.set(conn, key, str(current))
        return f"ENC-{year}-{current:04d}"

    def create_order(self, payload: dict) -> str:
        items = payload.get("items") or []
        if not items:
            raise ValueError("A encomenda precisa de itens")
        with db.transaction() as conn:
            payload = dict(payload)
            payload["numero"] = self._next_order_number(conn)
            oid = self.order_repo.create_order(conn, payload)

            subtotal = 0.0
            for it in items:
                product = self.product_repo.get(conn, it["product_id"])
                if not product:
                    raise ValueError("Produto inválido")
                qty = int(it["quantidade"])
                if qty <= 0:
                    raise ValueError("Quantidade deve ser > 0")
                stock_deducted = 0
                if product["tipo_producao"] == "stock_fisico":
                    if product["stock"] < qty:
                        raise ValueError(f"Stock insuficiente para {product['sku']}")
                    self.product_repo.update_stock(conn, product["id"], -qty)
                    stock_deducted = 1
                elif product["tipo_producao"] == "misto" and product["stock"] >= qty:
                    self.product_repo.update_stock(conn, product["id"], -qty)
                    stock_deducted = 1
                subtotal += qty * float(it["preco_unit"])
                self.order_repo.add_item(
                    conn,
                    {
                        "order_id": oid,
                        "product_id": product["id"],
                        "quantidade": qty,
                        "preco_unit": it["preco_unit"],
                        "tamanho": it.get("tamanho"),
                        "personalizacao": it.get("personalizacao"),
                        "stock_deducted": stock_deducted,
                    },
                )
            total = subtotal + float(payload.get("portes") or 0)
            conn.execute("UPDATE orders SET subtotal=?, total=? WHERE id=?", (subtotal, total, oid))
            self.log_repo.add(conn, "order_created", f"order={oid}")
            return oid

    def set_paid(self, order_id: str, paid: bool) -> None:
        with db.transaction() as conn:
            self.order_repo.set_paid(conn, order_id, 1 if paid else 0)

    def update_states(self, order_id: str, estado_comercial: str, estado_producao: str, estado_envio: str) -> None:
        if estado_comercial not in ORDER_STATES_COMMERCIAL:
            raise ValueError("Estado comercial inválido")
        if estado_producao not in ORDER_STATES_PRODUCTION:
            raise ValueError("Estado produção inválido")
        if estado_envio not in ORDER_STATES_SHIPPING:
            raise ValueError("Estado envio inválido")
        with db.transaction() as conn:
            self.order_repo.update_states(conn, order_id, estado_comercial, estado_producao, estado_envio)

    def update_tracking(self, order_id: str, tracking: str) -> None:
        with db.transaction() as conn:
            self.order_repo.update_tracking(conn, order_id, tracking)


    def duplicate_order(self, order_id: str) -> str:
        data = self.get_order_detail(order_id)
        o = data["order"]
        items = [
            {
                "product_id": it["product_id"],
                "quantidade": it["quantidade"],
                "preco_unit": it["preco_unit"],
                "tamanho": it.get("tamanho"),
                "personalizacao": it.get("personalizacao"),
            }
            for it in data["items"]
        ]
        return self.create_order(
            {
                "client_id": o["client_id"],
                "estado_comercial": ORDER_STATES_COMMERCIAL[0],
                "estado_producao": ORDER_STATES_PRODUCTION[0],
                "estado_envio": ORDER_STATES_SHIPPING[0],
                "portes": o.get("portes") or 0,
                "items": items,
            }
        )
    def cancel_order(self, order_id: str) -> None:
        with db.transaction() as conn:
            items = self.order_repo.get_items(conn, order_id)
            for item in items:
                if item["stock_deducted"] and not item["stock_returned"]:
                    self.product_repo.update_stock(conn, item["product_id"], item["quantidade"])
                    self.order_repo.mark_item_returned(conn, item["id"])
            self.order_repo.mark_canceled(conn, order_id)
            self.log_repo.add(conn, "order_canceled", f"order={order_id}")
