from __future__ import annotations

import sqlite3
import uuid

from utils import ts_now


class OrderRepository:
    def list_orders(self, conn: sqlite3.Connection, filters: dict) -> list[sqlite3.Row]:
        sql = """
            SELECT o.*, c.nome AS cliente_nome
            FROM orders o
            JOIN clients c ON c.id = o.client_id
            WHERE 1=1
        """
        args: list = []
        if filters.get("search"):
            sql += " AND (o.numero LIKE ? OR c.nome LIKE ?)"
            s = f"%{filters['search']}%"
            args.extend([s, s])
        for f in ("estado_comercial", "estado_producao", "estado_envio"):
            if filters.get(f):
                sql += f" AND o.{f}=?"
                args.append(filters[f])
        if filters.get("pago") is not None:
            sql += " AND o.pago=?"
            args.append(filters["pago"])
        sql += " ORDER BY o.created_at DESC"
        return conn.execute(sql, args).fetchall()

    def create_order(self, conn: sqlite3.Connection, payload: dict) -> str:
        oid = str(uuid.uuid4())
        now = ts_now()
        conn.execute(
            """
            INSERT INTO orders(id,numero,client_id,estado_comercial,estado_producao,estado_envio,pago,tracking,prazo_envio,notas,subtotal,portes,total,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                oid,
                payload["numero"],
                payload["client_id"],
                payload["estado_comercial"],
                payload["estado_producao"],
                payload["estado_envio"],
                payload.get("pago", 0),
                payload.get("tracking"),
                payload.get("prazo_envio"),
                payload.get("notas"),
                payload.get("subtotal", 0),
                payload.get("portes", 0),
                payload.get("total", 0),
                now,
                now,
            ),
        )
        return oid

    def add_item(self, conn: sqlite3.Connection, payload: dict) -> str:
        iid = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO order_items(id,order_id,product_id,quantidade,preco_unit,tamanho,personalizacao,stock_deducted,stock_returned,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                iid,
                payload["order_id"],
                payload["product_id"],
                payload["quantidade"],
                payload["preco_unit"],
                payload.get("tamanho"),
                payload.get("personalizacao"),
                payload.get("stock_deducted", 0),
                0,
                ts_now(),
            ),
        )
        return iid

    def get_order(self, conn: sqlite3.Connection, order_id: str):
        return conn.execute(
            """
            SELECT o.*, c.nome AS cliente_nome, c.telefone AS cliente_telefone, c.email AS cliente_email, c.morada AS cliente_morada
            FROM orders o JOIN clients c ON c.id=o.client_id WHERE o.id=?
            """,
            (order_id,),
        ).fetchone()

    def get_items(self, conn: sqlite3.Connection, order_id: str) -> list[sqlite3.Row]:
        return conn.execute(
            """
            SELECT i.*, p.sku, p.nome, p.tipo_producao
            FROM order_items i JOIN products p ON p.id=i.product_id
            WHERE i.order_id=?
            """,
            (order_id,),
        ).fetchall()

    def set_paid(self, conn: sqlite3.Connection, order_id: str, paid: int) -> None:
        conn.execute("UPDATE orders SET pago=?,updated_at=? WHERE id=?", (paid, ts_now(), order_id))

    def update_states(self, conn: sqlite3.Connection, order_id: str, ec: str, ep: str, ee: str) -> None:
        conn.execute(
            "UPDATE orders SET estado_comercial=?,estado_producao=?,estado_envio=?,updated_at=? WHERE id=?",
            (ec, ep, ee, ts_now(), order_id),
        )

    def update_tracking(self, conn: sqlite3.Connection, order_id: str, tracking: str) -> None:
        conn.execute("UPDATE orders SET tracking=?,updated_at=? WHERE id=?", (tracking, ts_now(), order_id))

    def mark_canceled(self, conn: sqlite3.Connection, order_id: str) -> None:
        conn.execute("UPDATE orders SET estado_comercial='cancelada', updated_at=? WHERE id=?", (ts_now(), order_id))

    def mark_item_returned(self, conn: sqlite3.Connection, item_id: str) -> None:
        conn.execute("UPDATE order_items SET stock_returned=1 WHERE id=?", (item_id,))
