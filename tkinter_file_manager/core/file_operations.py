import os
import stat
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

def get_dir_content(path: Path) -> List[Dict[str, any]]:
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a directory")

    contents = []

    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    _stat = entry.stat()
                    item = {
                        "name": entry.name,
                        "path": Path(entry.path),
                        "is_dir": entry.is_dir(),
                        "size": _stat.st_size if not entry.is_dir() else 0,
                        "modified": datetime.fromtimestamp(_stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "is_hidden": _is_hidden(entry),
                        "extension": _get_extension(entry)
                    }
                    contents.append(item)
                except (OSError, PermissionError) as e:
                    continue
    except OSError as e:
        raise RuntimeError(f"Scan file error {e}")

    return sorted(contents, key = lambda x:(not x["is_dir"], x["name"].lower()))


def _is_hidden(entry: os.DirEntry) -> bool:
    """
    跨平台隐藏文件检测
    适用于 Windows/Linux/macOS
    """
    path = Path(entry.path)

    # 1. 处理符号链接（读取目标而非链接本身）
    try:
        if entry.is_symlink():
            path = path.resolve()
    except OSError:
        pass  # 无法解析的链接视为普通文件

    # 2. Unix-like 系统：以点开头的文件/目录
    if entry.name.startswith('.'):
        return True

    # 3. Windows 隐藏属性检测
    try:
        # 优先使用 DirEntry 自带的 stat 避免额外系统调用
        st = entry.stat(follow_symlinks=False)

        # Windows 隐藏属性检测
        if hasattr(st, 'st_file_attributes'):
            hidden_bit = stat.FILE_ATTRIBUTE_HIDDEN
            return bool(st.st_file_attributes & hidden_bit)

        # macOS/BSD 隐藏标志 (chflags)
        if hasattr(st, 'st_flags'):
            # 0x8000 是 macOS 的 UF_HIDDEN 标志
            return bool(st.st_flags & 0x8000)

    except (AttributeError, OSError, FileNotFoundError):
        # 权限不足、文件不存在等情况
        pass

    # 4. Windows 特殊路径检测
    if os.name == 'nt':
        # 检查是否是系统保留路径
        return any(
            path.match(pattern)
            for pattern in [
                "$RECYCLE.BIN",
                "System Volume Information",
                "Thumbs.db",
                "~*"
            ]
        )

    return False

def _get_extension(entry:os.DirEntry) -> str:
    if entry.is_dir():
        return 'folder'
    return os.path.splitext(entry.name)[1].lower()