from __future__ import annotations

import sqlite3
import uuid

from utils import ts_now


class ProductRepository:
    def list_all(self, conn: sqlite3.Connection) -> list[sqlite3.Row]:
        return conn.execute("SELECT * FROM products ORDER BY nome").fetchall()

    def by_sku(self, conn: sqlite3.Connection, sku: str):
        return conn.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()

    def get(self, conn: sqlite3.Connection, product_id: str):
        return conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()

    def create(self, conn: sqlite3.Connection, payload: dict) -> str:
        pid = str(uuid.uuid4())
        now = ts_now()
        conn.execute(
            """
            INSERT INTO products(id,sku,nome,tipo_producao,preco,custo,stock,image_file,design_file,ativo,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                pid,
                payload["sku"],
                payload["nome"],
                payload["tipo_producao"],
                payload.get("preco", 0),
                payload.get("custo", 0),
                payload.get("stock", 0),
                payload.get("image_file"),
                payload.get("design_file"),
                1,
                now,
                now,
            ),
        )
        return pid

    def update_stock(self, conn: sqlite3.Connection, product_id: str, delta: int) -> None:
        conn.execute("UPDATE products SET stock = stock + ?, updated_at=? WHERE id=?", (delta, ts_now(), product_id))
