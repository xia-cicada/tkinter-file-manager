import customtkinter as ctk
from pathlib import Path
from typing import Dict
from tkinter_file_manager.gui.utils.icon_infos import EXTENSION_ICON_MAP, ICON_SIZES
from PIL import Image

class IconUtils:
    def __init__(self, icons_dir = "assets/icons"):
        self.icons_dir = Path(__file__).parent.parent.parent / icons_dir
        self._cache: Dict[str, ctk.CTkImage] = {}

        self._preload_icons()

    def _preload_icons(self):
        for icon_name in EXTENSION_ICON_MAP.keys():
            for size_name in ICON_SIZES.keys():
                self._cache[icon_name] = self._get_icon_image(EXTENSION_ICON_MAP[icon_name], size_name)

    def _get_icon_image(self, icon_name: str, size_name ='medium') -> ctk.CTkImage:
        cache_key = f"{icon_name}_{size_name}"
        if cache_key not in self._cache:
            icon_path = self._get_icon_path(icon_name)
            icon_image = Image.open(icon_path)
            icon_image.thumbnail(ICON_SIZES[size_name], Image.Resampling.LANCZOS)
            self._cache[cache_key] = ctk.CTkImage(icon_image, icon_image, ICON_SIZES[size_name])
        return self._cache[cache_key]

    def _get_icon_path(self, icon_name: str):
        icon_path = self.icons_dir / f"{icon_name}.png"

        if not icon_path.exists():
            icon_path = self.icons_dir / f"file.png"

        return icon_path

    def get_icon_by_ext(self, ext: str, size_name = 'small'):
        ext = ext.lower()
        icon_name = EXTENSION_ICON_MAP.get(ext, 'file')
        return self._get_icon_image(icon_name, size_name)

common_icons = IconUtils()