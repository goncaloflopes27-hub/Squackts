from __future__ import annotations

import sqlite3
import uuid

from utils import ts_now


class ClientRepository:
    def list_all(self, conn: sqlite3.Connection) -> list[sqlite3.Row]:
        return conn.execute("SELECT * FROM clients ORDER BY nome").fetchall()

    def create(self, conn: sqlite3.Connection, payload: dict) -> str:
        cid = str(uuid.uuid4())
        now = ts_now()
        conn.execute(
            """
            INSERT INTO clients(id,nome,telefone,email,nif,morada,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (cid, payload["nome"], payload.get("telefone"), payload.get("email"), payload.get("nif"), payload.get("morada"), now, now),
        )
        return cid
