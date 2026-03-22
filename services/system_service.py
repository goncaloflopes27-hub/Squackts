from __future__ import annotations

from pathlib import Path

import db


class SystemService:
    def __init__(self, log_repo):
        self.log_repo = log_repo

    def create_backup(self) -> Path:
        target = db.backup_to()
        with db.transaction() as conn:
            self.log_repo.add(conn, "backup_created", f"path={target}")
        return target
