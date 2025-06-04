#!/usr/bin/env python3
"""
创建大文件用于测试进度跟踪功能
"""

def create_large_test_file(filename: str, size: int = 5000):
    """创建包含指定数量行的测试文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(size):
            f.write(f"大文件测试文本数据 {i} - 这是用于验证进度跟踪功能的测试文本，包含一些中文字符以测试编码处理\n")
    
    print(f"已创建测试文件: {filename}, 包含 {size} 行数据")

if __name__ == "__main__":
    create_large_test_file("tmp/large_test_data.txt", 5000) 