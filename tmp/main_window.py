import customtkinter as ctk
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from PIL import Image, ImageTk
import os

from customtkinter import CTkImage

from thinker_file_manager.core.file_operations import get_dir_content  # 假设您的函数在file_ops.py中


class TreeItem:
    def __init__(self, path: Path, name: str, is_dir: bool, parent=None, expanded=False):
        self.path = path
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.expanded = expanded
        self.children = []
        self.widgets = {}  # 存储关联的UI组件


class FileManagerWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 窗口配置
        self.title("Modern File Manager")
        self.geometry("1200x800")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # 图标资源
        self._load_icons()

        # 布局配置
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 创建UI组件
        self._create_header()
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()

        # 初始化显示用户主目录
        self.navigate_to(Path.home())

    def _load_icons(self):
        """加载图标资源"""
        icon_size = (20, 20)
        self.icons = {
            "folder": self._create_icon("📁", icon_size),
            "folder_open": self._create_icon("📂", icon_size),
            "file": self._create_icon("📄", icon_size),
            "home": self._create_icon("🏠", icon_size),
            "disk": self._create_icon("💽", icon_size),
            "back": self._create_icon("⬅️", icon_size),
            "forward": self._create_icon("➡️", icon_size),
            "up": self._create_icon("⬆️", icon_size),
            "refresh": self._create_icon("🔄", icon_size),
            "chevron_right": self._create_icon("▶", icon_size),
            "chevron_down": self._create_icon("▼", icon_size),
        }

    def _create_icon(self, emoji: str, size: tuple[int, int]) -> CTkImage:
        """创建表情符号图标"""
        from PIL import Image, ImageDraw, ImageFont
        try:
            font = ImageFont.truetype("seguiemj.ttf", 16)  # Windows表情符号字体
        except:
            font = ImageFont.load_default()
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), emoji, font=font, embedded_color=True)
        return CTkImage(image)

    def _create_header(self):
        """创建顶部导航栏"""
        header_frame = ctk.CTkFrame(self, height=40)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # 导航按钮
        ctk.CTkButton(header_frame, image=self.icons["back"], text="", width=30, command=self._go_back).pack(
            side="left", padx=2)
        ctk.CTkButton(header_frame, image=self.icons["forward"], text="", width=30, command=self._go_forward).pack(
            side="left", padx=2)
        ctk.CTkButton(header_frame, image=self.icons["up"], text="", width=30, command=self._go_up).pack(side="left",
                                                                                                         padx=2)
        ctk.CTkButton(header_frame, image=self.icons["refresh"], text="", width=30, command=self._refresh).pack(
            side="left", padx=2)

        # 地址栏
        self.address_bar = ctk.CTkEntry(header_frame)
        self.address_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.address_bar.bind("<Return>", lambda e: self._on_address_bar_enter())

        # 搜索框
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right", padx=5)
        ctk.CTkLabel(search_frame, text="🔍").pack(side="left")
        self.search_entry = ctk.CTkEntry(search_frame, width=150, placeholder_text="Search...")
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self._on_search())

    def _create_sidebar(self):
        """创建左侧树形目录栏"""
        sidebar_frame = ctk.CTkFrame(self, width=250)
        sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        sidebar_frame.grid_propagate(False)

        # 快速访问区域
        quick_access = ctk.CTkLabel(sidebar_frame, text="Quick Access", anchor="w")
        quick_access.pack(fill="x", padx=5, pady=(5, 0))

        quick_items = [
            ("Home", Path.home()),
            ("Desktop", Path.home() / "Desktop"),
            ("Documents", Path.home() / "Documents"),
            ("Downloads", Path.home() / "Downloads"),
        ]

        for name, path in quick_items:
            btn = ctk.CTkButton(
                sidebar_frame,
                text=name,
                image=self.icons["home"] if name == "Home" else self.icons["folder"],
                anchor="w",
                command=lambda p=path: self.navigate_to(p)
            )
            btn.pack(fill="x", padx=5, pady=2)

        # 驱动器列表
        drives_frame = ctk.CTkFrame(sidebar_frame)
        drives_frame.pack(fill="x", padx=5, pady=(10, 0))
        ctk.CTkLabel(drives_frame, text="Drives", anchor="w").pack(fill="x")

        for drive in self._get_drives():
            btn = ctk.CTkButton(
                drives_frame,
                text=f"{drive}",
                image=self.icons["disk"],
                anchor="w",
                command=lambda d=drive: self.navigate_to(Path(d))
            )
            btn.pack(fill="x", padx=5, pady=2)

        # 树形目录容器
        self.tree_container = ctk.CTkScrollableFrame(sidebar_frame)
        self.tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        # 树形目录数据
        self.tree_items = {}  # path_str: TreeItem
        self.root_items = []

    def _get_drives(self) -> List[str]:
        """获取系统驱动器列表"""
        if os.name == 'nt':  # Windows
            import string
            return [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        else:  # Unix-like
            return ["/"]

    def _create_main_content(self):
        """创建主内容区域"""
        # 主内容框架
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # 列标题
        header_frame = ctk.CTkFrame(content_frame, height=30)
        header_frame.pack(fill="x")

        ctk.CTkLabel(header_frame, text="Name", width=300, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_frame, text="Size", width=100, anchor="e").grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(header_frame, text="Modified", width=150, anchor="w").grid(row=0, column=2, sticky="w")

        # 文件列表
        self.file_list_frame = ctk.CTkScrollableFrame(content_frame)
        self.file_list_frame.pack(fill="both", expand=True)

        # 当前路径和历史记录
        self.current_path = None
        self.history = []
        self.history_index = -1

    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ctk.CTkFrame(self, height=25)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.status_label = ctk.CTkLabel(status_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True, padx=5)

        self.selection_label = ctk.CTkLabel(status_frame, text="0 items selected", anchor="e")
        self.selection_label.pack(side="right", padx=5)

    def navigate_to(self, path: Path):
        """导航到指定路径"""
        try:
            # 更新当前路径
            self.current_path = path.resolve()
            self.address_bar.delete(0, "end")
            self.address_bar.insert(0, str(self.current_path))

            # 添加到历史记录
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(str(self.current_path))
            self.history_index += 1

            # 更新文件列表
            self._update_file_list()

            # 更新树形目录
            self._update_tree_view()

            # 更新状态栏
            self.status_label.configure(text=f"Viewing: {self.current_path}")

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")

    def _update_file_list(self):
        """更新文件列表显示"""
        # 清空当前列表
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        # 获取目录内容
        try:
            contents = get_dir_content(self.current_path)

            # 创建列表项
            for i, item in enumerate(contents):
                row_frame = ctk.CTkFrame(self.file_list_frame)
                row_frame.pack(fill="x", pady=1)

                # 名称列
                icon = self.icons["folder"] if item["is_dir"] else self.icons["file"]
                name_label = ctk.CTkLabel(
                    row_frame,
                    text=item["name"],
                    image=icon,
                    compound="left",
                    anchor="w",
                    width=300
                )
                name_label.grid(row=0, column=0, sticky="w")

                # 大小列
                size_text = f"{item['size']:,} bytes" if not item["is_dir"] else ""
                size_label = ctk.CTkLabel(row_frame, text=size_text, anchor="e", width=100)
                size_label.grid(row=0, column=1, sticky="e")

                # 修改时间列
                mod_label = ctk.CTkLabel(row_frame, text=item["modified"], anchor="w", width=150)
                mod_label.grid(row=0, column=2, sticky="w")

                # 绑定点击事件
                row_frame.bind("<Button-1>", lambda e, idx=i: self._on_file_select(idx))
                name_label.bind("<Button-1>", lambda e, idx=i: self._on_file_select(idx))
                size_label.bind("<Button-1>", lambda e, idx=i: self._on_file_select(idx))
                mod_label.bind("<Button-1>", lambda e, idx=i: self._on_file_select(idx))

                # 绑定双击事件
                if item["is_dir"]:
                    row_frame.bind("<Double-1>", lambda e, p=item["path"]: self.navigate_to(p))
                    name_label.bind("<Double-1>", lambda e, p=item["path"]: self.navigate_to(p))

            # 更新选择计数
            self.selection_label.configure(text=f"{len(contents)} items")

        except Exception as e:
            self.status_label.configure(text=f"Error reading directory: {str(e)}")

    def _update_tree_view(self):
        """更新树形目录视图"""
        # 清空当前树形结构
        for widget in self.tree_container.winfo_children():
            widget.destroy()

        self.tree_items = {}
        self.root_items = []

        # 添加当前路径及其父路径
        parts = []
        parent = self.current_path
        while parent and parent != parent.parent:  # 避免无限循环
            parts.insert(0, parent)
            parent = parent.parent

        # 构建树形结构
        for i, path in enumerate(parts):
            parent_item = None if i == 0 else self.tree_items.get(str(parts[i - 1]))

            item = TreeItem(
                path=path,
                name=path.name,
                is_dir=True,
                parent=parent_item,
                expanded=i == len(parts) - 1  # 自动展开当前路径
            )

            self.tree_items[str(path)] = item
            if parent_item is None:
                self.root_items.append(item)
            else:
                parent_item.children.append(item)

            # 如果是当前路径，添加子目录
            if i == len(parts) - 1:
                try:
                    for content in get_dir_content(path):
                        if content["is_dir"]:
                            child_item = TreeItem(
                                path=content["path"],
                                name=content["name"],
                                is_dir=True,
                                parent=item
                            )
                            item.children.append(child_item)
                            self.tree_items[str(content["path"])] = child_item
                except Exception:
                    pass

        # 渲染树形结构
        self._render_tree_items(self.root_items, 0)

    def _render_tree_items(self, items: List[TreeItem], level: int):
        """递归渲染树形结构"""
        for item in items:
            # 创建项目框架
            item_frame = ctk.CTkFrame(self.tree_container)
            item_frame.pack(fill="x", padx=(level * 15, 5), pady=1)

            # 存储UI组件引用
            item.widgets = {
                "frame": item_frame,
                "toggle_btn": None,
                "name_btn": None
            }

            # 如果有子项，添加展开/折叠按钮
            if item.children:
                toggle_btn = ctk.CTkButton(
                    item_frame,
                    image=self.icons["chevron_down"] if item.expanded else self.icons["chevron_right"],
                    text="",
                    width=20,
                    height=20,
                    fg_color="transparent",
                    hover_color=("#f0f0f0", "#333333"),
                    command=lambda i=item: self._toggle_tree_item(i)
                )
                toggle_btn.pack(side="left")
                item.widgets["toggle_btn"] = toggle_btn
            else:
                # 占位符保持对齐
                spacer = ctk.CTkLabel(item_frame, text="", width=20)
                spacer.pack(side="left")

            # 名称按钮
            icon = self.icons["folder_open"] if item.expanded else self.icons["folder"]
            name_btn = ctk.CTkButton(
                item_frame,
                text=item.name,
                image=icon,
                compound="left",
                anchor="w",
                fg_color="transparent",
                hover_color=("#f0f0f0", "#333333"),
                command=lambda p=item.path: self.navigate_to(p)
            )
            name_btn.pack(side="left", fill="x", expand=True)
            item.widgets["name_btn"] = name_btn

            # 渲染子项（如果展开）
            if item.expanded and item.children:
                self._render_tree_items(item.children, level + 1)

    def _toggle_tree_item(self, item: TreeItem):
        """切换树形项目的展开/折叠状态"""
        item.expanded = not item.expanded

        # 更新图标
        if item.widgets["toggle_btn"]:
            item.widgets["toggle_btn"].configure(
                image=self.icons["chevron_down"] if item.expanded else self.icons["chevron_right"]
            )

        if item.widgets["name_btn"]:
            item.widgets["name_btn"].configure(
                image=self.icons["folder_open"] if item.expanded else self.icons["folder"]
            )

        # 重新渲染树形结构
        for widget in self.tree_container.winfo_children():
            widget.destroy()
        self._render_tree_items(self.root_items, 0)

    def _on_file_select(self, index):
        """文件列表项选择事件"""
        self.status_label.configure(text=f"Selected item {index}")

    def _on_address_bar_enter(self):
        """地址栏回车事件"""
        path = Path(self.address_bar.get())
        if path.exists():
            self.navigate_to(path)
        else:
            self.status_label.configure(text="Path does not exist")

    def _on_search(self):
        """搜索事件"""
        query = self.search_entry.get().lower()
        if not query:
            return

        self.status_label.configure(text=f"Searching for: {query}...")

    def _go_back(self):
        """后退导航"""
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate_to(Path(self.history[self.history_index]))

    def _go_forward(self):
        """前进导航"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.navigate_to(Path(self.history[self.history_index]))

    def _go_up(self):
        """向上导航"""
        if self.current_path and self.current_path.parent != self.current_path:
            self.navigate_to(self.current_path.parent)

    def _refresh(self):
        """刷新当前视图"""
        if self.current_path:
            self.navigate_to(self.current_path)


if __name__ == "__main__":
    app = FileManagerWindow()
    app.mainloop()