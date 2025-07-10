import os
import stat
from tempfile import TemporaryDirectory
from pathlib import Path
import pytest

from tkinter_file_manager.core.file_operations import get_dir_content


@pytest.fixture
def test_dir():
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        (root / "visible.txt").write_text("normal file")
        (root / ".hidden.txt").write_text("hidden file")
        (root / "normal_dir").mkdir()
        (root / "normal_dir" / "subfile.txt").write_text("sub file")

        if os.name == 'nt':
            hidden_attr = stat.FILE_ATTRIBUTE_HIDDEN
            (root / "system_hidden.txt").write_text("system hidden")
            os.chmod(root / "system_hidden.txt", hidden_attr)

        yield root


def test_basic_directory_structure(test_dir):
    """测试基本目录结构扫描"""
    contents = get_dir_content(test_dir)

    # 验证返回类型和基本字段
    assert isinstance(contents, list)
    assert all(isinstance(item, dict) for item in contents)
    assert all("name" in item and "path" in item for item in contents)

    # 验证找到的文件和目录
    names = {item["name"] for item in contents}
    assert "visible.txt" in names
    assert "normal_dir" in names
    assert ".hidden.txt" in names


def test_file_properties(test_dir):
    """测试文件属性准确性"""
    visible_file = next(
        item for item in get_dir_content(test_dir)
        if item["name"] == "visible.txt"
    )

    assert visible_file["is_dir"] is False
    assert visible_file["size"] == len("normal file")
    assert visible_file["extension"] == ".txt"
    assert visible_file["is_hidden"] is False


def test_directory_properties(test_dir):
    """测试目录属性准确性"""
    dir_item = next(
        item for item in get_dir_content(test_dir)
        if item["name"] == "normal_dir"
    )

    assert dir_item["is_dir"] is True
    assert dir_item["size"] == 0
    assert dir_item["extension"] == ""


def test_hidden_files_unix(test_dir):
    """测试Unix风格隐藏文件"""
    hidden_item = next(
        item for item in get_dir_content(test_dir)
        if item["name"] == ".hidden.txt"
    )
    assert hidden_item["is_hidden"] is True


@pytest.mark.skipif(os.name != 'nt', reason="仅测试Windows隐藏属性")
def test_windows_hidden_files(test_dir):
    """测试Windows系统隐藏文件"""
    hidden_item = next(
        item for item in get_dir_content(test_dir)
        if item["name"] == "system_hidden.txt"
    )
    assert hidden_item["is_hidden"] is True


def test_nonexistent_directory():
    """测试不存在的目录"""
    with pytest.raises(NotADirectoryError):
        get_dir_content(Path("/nonexistent/path"))


def test_permission_denied():
    """测试无权限目录（需要模拟环境）"""
    if os.name == 'posix':
        with TemporaryDirectory() as tmpdir:
            protected_dir = Path(tmpdir) / "restricted"
            protected_dir.mkdir()
            os.chmod(protected_dir, 0o000)  # 移除所有权限

            try:
                # 应该跳过无权限目录而非抛出异常
                result = get_dir_content(Path(tmpdir))
                assert not any(item["name"] == "restricted" for item in result)
            finally:
                os.chmod(protected_dir, 0o755)  # 恢复权限


def test_sorting_order(test_dir):
    """测试目录优先的排序"""
    contents = get_dir_content(test_dir)
    dir_positions = [
        i for i, item in enumerate(contents)
        if item["is_dir"]
    ]

    # 验证所有目录排在非目录前面
    assert all(
        pos < non_dir_pos
        for pos in dir_positions
        for non_dir_pos in range(len(contents))
        if not contents[non_dir_pos]["is_dir"]
    )


def test_case_insensitive_sort(test_dir):
    """测试大小写不敏感的排序"""
    (test_dir / "a.txt").touch()
    (test_dir / "Z.txt").touch()

    names = [item["name"] for item in get_dir_content(test_dir)]
    assert names.index("a.txt") < names.index("Z.txt")


def test_large_directory_performance(benchmark, test_dir):
    """基准测试（需要pytest-benchmark）"""
    # 创建1000个测试文件
    for i in range(1000):
        (test_dir / f"test_{i}.txt").touch()

    benchmark(get_dir_content, test_dir)
