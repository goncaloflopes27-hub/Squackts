from __future__ import annotations

import re
import shutil
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

_MONEY_Q = Decimal("0.01")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def ts_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def simple_email_valid(email: str) -> bool:
    if not email:
        return True
    return _EMAIL_RE.match(email.strip()) is not None


def nif_valid(nif: str) -> bool:
    if not nif:
        return True
    digits = re.sub(r"\D", "", nif)
    return len(digits) == 9 and digits.isdigit()


def to_int(value: Any, default: int = 0, *, min_value: int | None = None) -> int:
    try:
        i = int(str(value).strip())
    except Exception:
        i = default
    if min_value is not None and i < min_value:
        return min_value
    return i


def to_bool_int(value: Any) -> int:
    return 1 if bool(value) else 0


def to_money_decimal(value: Any, default: Decimal = Decimal("0.00")) -> Decimal:
    try:
        if value is None:
            return default
        if isinstance(value, Decimal):
            d = value
        else:
            s = str(value).strip().replace(" ", "").replace(",", ".")
            if s == "":
                return default
            d = Decimal(s)
        return d.quantize(_MONEY_Q, rounding=ROUND_HALF_UP)
    except Exception:
        return default


def money_to_float(value: Any) -> float:
    return float(to_money_decimal(value))


def copy_file_unique(src_path: str, dest_dir: Path) -> str:
    if not src_path:
        return ""
    src = Path(src_path)
    if not src.exists():
        return ""
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / src.name
    if dest.exists():
        base, ext = dest.stem, dest.suffix
        i = 1
        while True:
            cand = dest_dir / f"{base}_{i}{ext}"
            if not cand.exists():
                dest = cand
                break
            i += 1
    shutil.copy2(src, dest)
    return dest.name
