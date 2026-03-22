from __future__ import annotations

import db


class ProductionService:
    def __init__(self, order_repo):
        self.order_repo = order_repo

    def queue(self, *, limit: int = 100) -> list[dict]:
        filters = {
            "estado_comercial": "paga",
            "estado_envio": "por enviar",
        }
        with db.connect() as conn:
            rows = self.order_repo.list_orders(conn, filters)
            return [dict(r) for r in rows[:limit]]
