from __future__ import annotations

import db
from config import PRODUCTION_TYPES


class ProductService:
    def __init__(self, repo, log_repo):
        self.repo = repo
        self.log_repo = log_repo

    def list_products(self):
        with db.connect() as conn:
            return [dict(r) for r in self.repo.list_all(conn)]

    def create_product(self, payload: dict) -> str:
        if payload.get("tipo_producao") not in PRODUCTION_TYPES:
            raise ValueError("Tipo de produção inválido")
        if self.sku_exists(payload.get("sku", "")):
            raise ValueError("SKU já existe")
        with db.transaction() as conn:
            pid = self.repo.create(conn, payload)
            self.log_repo.add(conn, "product_created", f"product={pid}")
            return pid

    def sku_exists(self, sku: str) -> bool:
        with db.connect() as conn:
            return self.repo.by_sku(conn, sku) is not None
