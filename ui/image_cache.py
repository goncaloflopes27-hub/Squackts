from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from PIL import Image, ImageTk


class ImageCache:
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._cache: OrderedDict[tuple[str, int, int], ImageTk.PhotoImage] = OrderedDict()

    def get_thumb(self, path: str, width: int = 96, height: int = 96):
        key = (path, width, height)
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        p = Path(path)
        if not p.exists():
            return None
        img = Image.open(p).convert("RGBA")
        img.thumbnail((width, height))
        tk_img = ImageTk.PhotoImage(img)
        self._cache[key] = tk_img
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
        return tk_img
