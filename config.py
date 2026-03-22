from __future__ import annotations

from pathlib import Path
import os

APP_NAME = "SquackTS Enterprise"

BRAND_YELLOW = "#F5A300"
BRAND_BLACK = "#1A1A1A"
BRAND_WHITE = "#FFFFFF"
BG_LIGHT = "#F2F2F2"

ORDER_STATES_COMMERCIAL = ["rascunho", "aguarda pagamento", "paga", "cancelada"]
ORDER_STATES_PRODUCTION = ["pendente", "em produção", "produzida"]
ORDER_STATES_SHIPPING = ["por enviar", "enviada", "entregue"]
PRODUCTION_TYPES = ["print_on_demand", "stock_fisico", "misto"]

PROJECT_DIR = Path(__file__).resolve().parent
IMAGES_DIR = PROJECT_DIR / "images"
BACKUPS_DIR = PROJECT_DIR / "backups"

_local_appdata = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
DATA_DIR = Path(os.environ.get("SQUACKTS_DATA_DIR", str(Path(_local_appdata) / "SquackTS_Enterprise" / "data")))
DB_PATH = Path(os.environ.get("SQUACKTS_DB_PATH", str(DATA_DIR / "squackts_enterprise.db")))
