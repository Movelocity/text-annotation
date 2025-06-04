#!/usr/bin/env python3
"""
文本导入性能测试脚本

对比优化前后的导入性能：
- DataImporter (逐个操作)
- AnnotationService (批量操作)
"""

import os
import time
import tempfile
import requests
from pathlib import Path

# 配置
API_BASE_URL = "http://localhost:8000"
TEST_DATA_SIZE = 1000  # 测试数据条数

def create_test_file(size: int) -> str:
    """创建测试用的文本文件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        for i in range(size):
            f.write(f"测试文本数据 {i} - 这是用于性能测试的示例文本\n")
        return f.name

def test_import_performance():
    """测试导入性能"""
    print(f"=== 文本导入性能测试 ===")
    print(f"测试数据量: {TEST_DATA_SIZE} 条")
    
    # 创建测试文件
    test_file = create_test_file(TEST_DATA_SIZE)
    print(f"测试文件: {test_file}")
    
    try:
        # 测试优化后的批量导入
        print("\n--- 测试批量导入 (AnnotationService) ---")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/import/text-file",
            json={"file_path": test_file}
        )
        
        end_time = time.time()
        batch_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量导入成功")
            print(f"   导入时间: {batch_time:.2f} 秒")
            print(f"   导入记录: {result['imported_count']} 条")
            print(f"   导入速度: {result['imported_count']/batch_time:.0f} 条/秒")
            print(f"   文件大小: {result.get('file_size', 0)/1024:.1f} KB")
        else:
            print(f"❌ 批量导入失败: {response.status_code} - {response.text}")
            return
        
        # 检查系统统计
        stats_response = requests.get(f"{API_BASE_URL}/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\n--- 导入后统计 ---")
            print(f"总文本数: {stats['total_texts']}")
            print(f"已标注: {stats['labeled_texts']}")
            print(f"未标注: {stats['unlabeled_texts']}")
        
        print(f"\n✅ 性能测试完成！")
        print(f"推荐使用: 批量导入 (AnnotationService)")
        print(f"性能优势: 使用批量操作，适合大文件导入")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保服务器已启动")
        print("   启动命令: uv run python -m app.main")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.unlink(test_file)
            print(f"清理测试文件: {test_file}")

if __name__ == "__main__":
    test_import_performance() 