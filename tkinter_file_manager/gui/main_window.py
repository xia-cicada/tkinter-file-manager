import customtkinter as ctk

from core.file_operations import get_dir_content
from tkinter_file_manager.gui.components.file_list import FileListPanel
from pathlib import Path
from tkinter_file_manager.gui.event_bus import signal_path_change
from tkinter_file_manager.gui.utils.ui_button import UIButton


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File Manager")
        self.geometry("800x600")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.current_path = Path("D:/")
        self._create_ui()

    def _navigate_to(self, path: Path):
        self.current_path = path
        signal_path_change.send(self.current_path)

    def _create_ui(self):
        self.main_panel = ctk.CTkFrame(self)
        self.main_panel.pack(fill="both", expand=True)
        self._create_address_bar()
        self._create_toolbar()
        self._create_body()
        self._create_status_bar()

        self._navigate_to(self.current_path)

    def _create_address_bar(self):
        address_bar = ctk.CTkFrame(
            master=self.main_panel,
            corner_radius=6,
            bg_color="#ffffff",
        )
        address_bar.pack(fill="x",padx=5,pady=5)
        content = ctk.CTkFrame(address_bar)
        content.pack(fill="both", expand=True)
        pre_button = UIButton(content, "left")
        forward_button = UIButton(content, "right")
        refresh_button = UIButton(content, "refresh")
        pre_button.grid(row=0, column=0)
        forward_button.grid(row=0, column=1)
        refresh_button.grid(row=0, column=2)

    def _create_toolbar(self):
        pass

    def _create_body(self):
        self.body_panel = ctk.CTkFrame(self.main_panel)
        self.body_panel.pack(fill="both", expand=True)
        self._create_navigation_panel()
        self._create_content_panel()
        self._create_preview_panel()

    def _create_status_bar(self):
        pass

    def _create_navigation_panel(self):
        pass

    def _create_content_panel(self):
        content_panel = ctk.CTkFrame(self.body_panel)
        content_panel.pack(fill="both", expand=True)
        self.file_list = FileListPanel(content_panel)

    def _create_preview_panel(self):
        pass
