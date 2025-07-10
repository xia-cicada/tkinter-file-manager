from pathlib import Path

import customtkinter as ctk

from core.file_operations import get_dir_content
from gui.utils.icon_utils import common_icons
from tkinter_file_manager.gui.event_bus import signal_status_change, signal_path_change


class FileListPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.current_path = Path()
        self.files = []
        signal_path_change.connect(self.refresh)

    def refresh(self, path: Path):
        self.current_path = path
        self.clear()

        try:
            self.files = get_dir_content(path)
            for i, item in enumerate(self.files):
                row = ctk.CTkFrame(self)
                row.pack(fill="x", pady=1)
                icon = common_icons.get_icon_by_ext(item["extension"])
                name_label = ctk.CTkLabel(
                    row,
                    text=item["name"],
                    image=icon,
                    compound="left",
                    anchor="w",
                    width=300
                )
                name_label.grid(row=0, column=0, sticky="w")

                size_text = f"{item['size']:,} bytes" if not item["is_dir"] else ""
                size_label = ctk.CTkLabel(row, text=size_text, anchor="e", width=100)
                size_label.grid(row=0, column=1, sticky="e")

                mod_label = ctk.CTkLabel(row, text=item["modified"], anchor="w", width=150)
                mod_label.grid(row=0, column=2, sticky="w")

                row.bind("<Double-Button-1>", lambda _e, idx=i: self._on_row_double_click(idx))
                name_label.bind("<Double-Button-1>", lambda _e, idx=i: self._on_row_double_click(idx))
                size_label.bind("<Double-Button-1>", lambda _e, idx=i: self._on_row_double_click(idx))
                size_label.bind("<Double-Button-1>", lambda _e, idx=i: self._on_row_double_click(idx))
                mod_label.bind("<Double-Button-1>", lambda _e, idx=i: self._on_row_double_click(idx))

        except Exception as e:
            signal_status_change.send(f"Error reading directory: {str(e)}")
            self.clear()

    def clear(self):
        for child in self.winfo_children():
            child.destroy()

    def _on_row_double_click(self, idx: int):
        file = self.files[idx]
        if not file["is_dir"]: return
        signal_path_change.send(file["path"])