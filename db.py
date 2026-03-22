from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from config import BACKUPS_DIR, DATA_DIR, DB_PATH, IMAGES_DIR
from schema import apply_schema


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    ensure_directories()
    conn = sqlite3.connect(path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    return conn


def init_database() -> None:
    with connect() as conn:
        apply_schema(conn)
        conn.commit()


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def backup_to(dest_path: Path | None = None) -> Path:
    ensure_directories()
    target = dest_path or (BACKUPS_DIR / f"squackts_enterprise_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    target.parent.mkdir(parents=True, exist_ok=True)
    with connect() as src, sqlite3.connect(target) as dst:
        src.backup(dst)
        dst.commit()
    return target
