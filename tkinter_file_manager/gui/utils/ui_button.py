import customtkinter as ctk
from tkinter_file_manager.gui.utils.icon_utils import common_icons

class UIButton(ctk.CTkButton):
    def __init__(self, parent, icon_name: str):
        icon = common_icons.get_icon_by_name(icon_name)
        super().__init__(
            parent,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            border_width=0,
            corner_radius=0,
            text="",
            width=30,
            image=icon
        )