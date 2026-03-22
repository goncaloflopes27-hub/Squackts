from __future__ import annotations

from pathlib import Path
from datetime import datetime

import db
from config import BACKUPS_DIR


class SystemService:
    def __init__(self, log_repo):
        self.log_repo = log_repo

    def create_backup(self) -> Path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = BACKUPS_DIR / f"squackts_enterprise_backup_{stamp}.db"
        with db.connect() as src, db.connect(target) as dst:
            src.backup(dst)
        return target
