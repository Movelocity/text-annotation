#!/usr/bin/env python3
"""
测试批量标签更新功能的脚本
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_bulk_update_labels():
    """测试批量标签更新功能"""
    
    print("=== 测试批量标签更新功能 ===\n")
    
    # 1. 创建一些测试数据
    print("1. 创建测试数据...")
    test_texts = [
        {"text": "客户询问订单状态", "labels": "customer_service"},
        {"text": "用户投诉产品质量问题", "labels": "complaint, product"},
        {"text": "咨询产品价格信息", "labels": "inquiry"},
        {"text": "要求退款退货", "labels": "refund"},
        {"text": "技术支持问题", "labels": "support"}
    ]
    
    created_ids = []
    for text_data in test_texts:
        try:
            response = requests.post(f"{BASE_URL}/annotations/", json=text_data)
            if response.status_code == 201:
                result = response.json()
                created_ids.append(result["id"])
                print(f"  创建记录 ID: {result['id']}, 文本: {result['text'][:20]}..., 标签: {result['labels']}")
            else:
                print(f"  创建失败: {response.text}")
        except Exception as e:
            print(f"  创建异常: {e}")
    
    if not created_ids:
        print("没有成功创建测试数据，退出测试")
        return
    
    print(f"\n成功创建 {len(created_ids)} 条测试数据\n")
    
    # 2. 测试通过ID列表批量添加标签
    print("2. 通过ID列表批量添加标签...")
    update_request = {
        "text_ids": created_ids[:3],  # 前3条记录
        "labels_to_add": "urgent, priority"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/annotations/bulk-update-labels", json=update_request)
        if response.status_code == 200:
            result = response.json()
            print(f"  成功: {result['message']}")
            print(f"  更新数量: {result['updated_count']}")
        else:
            print(f"  失败: {response.text}")
    except Exception as e:
        print(f"  异常: {e}")
    
    # 3. 测试通过搜索条件批量删除标签
    print("\n3. 通过搜索条件批量删除标签...")
    update_request = {
        "search_criteria": {
            "labels": "customer_service",
            "page": 1,
            "per_page": 50
        },
        "labels_to_remove": "customer_service"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/annotations/bulk-update-labels", json=update_request)
        if response.status_code == 200:
            result = response.json()
            print(f"  成功: {result['message']}")
            print(f"  更新数量: {result['updated_count']}")
        else:
            print(f"  失败: {response.text}")
    except Exception as e:
        print(f"  异常: {e}")
    
    # 4. 测试同时添加和删除标签
    print("\n4. 同时添加和删除标签...")
    update_request = {
        "text_ids": created_ids[-2:],  # 后2条记录
        "labels_to_add": "reviewed, verified",
        "labels_to_remove": "support"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/annotations/bulk-update-labels", json=update_request)
        if response.status_code == 200:
            result = response.json()
            print(f"  成功: {result['message']}")
            print(f"  更新数量: {result['updated_count']}")
        else:
            print(f"  失败: {response.text}")
    except Exception as e:
        print(f"  异常: {e}")
    
    # 5. 查看最终结果
    print("\n5. 查看更新后的数据...")
    for record_id in created_ids:
        try:
            response = requests.get(f"{BASE_URL}/annotations/{record_id}")
            if response.status_code == 200:
                result = response.json()
                print(f"  ID: {result['id']}, 文本: {result['text'][:30]}..., 标签: {result['labels']}")
            else:
                print(f"  获取记录 {record_id} 失败: {response.text}")
        except Exception as e:
            print(f"  异常: {e}")
    
    # 6. 测试错误情况
    print("\n6. 测试错误情况...")
    
    # 6.1 没有提供操作
    print("  6.1 测试没有提供任何操作的情况...")
    error_request = {
        "text_ids": [created_ids[0]]
    }
    try:
        response = requests.post(f"{BASE_URL}/annotations/bulk-update-labels", json=error_request)
        print(f"    状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"    错误信息: {response.json().get('detail', response.text)}")
    except Exception as e:
        print(f"    异常: {e}")
    
    # 6.2 没有提供目标数据
    print("  6.2 测试没有提供目标数据的情况...")
    error_request = {
        "labels_to_add": "test"
    }
    try:
        response = requests.post(f"{BASE_URL}/annotations/bulk-update-labels", json=error_request)
        print(f"    状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"    错误信息: {response.json().get('detail', response.text)}")
    except Exception as e:
        print(f"    异常: {e}")
    
    print("\n=== 测试完成 ===")


def cleanup_test_data():
    """清理测试数据（可选）"""
    print("\n=== 清理测试数据 ===")
    # 这里可以添加清理逻辑，比如删除创建的测试数据
    print("测试数据已保留用于手动检查")


if __name__ == "__main__":
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("服务器运行正常，开始测试...\n")
            test_bulk_update_labels()
            cleanup_test_data()
        else:
            print(f"服务器健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"无法连接到服务器 {BASE_URL}: {e}")
        print("请先启动服务器: uv run server") 