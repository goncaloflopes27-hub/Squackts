from __future__ import annotations

import sqlite3
import uuid

from utils import ts_now


class LogRepository:
    def add(self, conn: sqlite3.Connection, action: str, details: str = "", user: str = "system") -> None:
        conn.execute(
            "INSERT INTO logs(id,user,action,details,created_at) VALUES(?,?,?,?,?)",
            (str(uuid.uuid4()), user, action, details, ts_now()),
        )
