import sys
from pytest import main as pytest_main

def test():
    """包装pytest的入口函数"""
    sys.exit(pytest_main())