#!/usr/bin/env python3
"""
文本标注系统的演示脚本。

此脚本演示：
1. 搜索标注
2. 创建新标注
3. 批量标注
4. 获取统计信息
"""

import requests
import json
from typing import List, Dict

# API 基础 URL
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """打印格式化的章节标题。"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def search_annotations(query: str = None, labels: str = None, unlabeled_only: bool = False, 
                      page: int = 1, per_page: int = 5) -> Dict:
    """使用各种过滤器搜索标注。"""
    payload = {
        "page": page,
        "per_page": per_page,
        "unlabeled_only": unlabeled_only
    }
    
    if query:
        payload["query"] = query
    if labels:
        payload["labels"] = labels
        
    response = requests.post(f"{BASE_URL}/annotations/search", json=payload)
    return response.json()


def create_annotation(text: str, labels: str = None) -> Dict:
    """创建新标注。"""
    payload = {"text": text}
    if labels:
        payload["labels"] = labels
        
    response = requests.post(f"{BASE_URL}/annotations/", json=payload)
    return response.json()


def import_texts(texts: List[str]) -> Dict:
    """导入多个文本作为未标注数据。"""
    payload = {"texts": texts}
    response = requests.post(f"{BASE_URL}/annotations/import-texts", json=payload)
    return response.json()


def bulk_label(text_ids: List[int], labels: str) -> Dict:
    """为多个文本应用标签。"""
    payload = {"text_ids": text_ids, "labels": labels}
    response = requests.post(f"{BASE_URL}/annotations/bulk-label", json=payload)
    return response.json()


def get_system_stats() -> Dict:
    """获取系统统计信息。"""
    response = requests.get(f"{BASE_URL}/stats/system")
    return response.json()


def get_all_labels() -> List[Dict]:
    """获取所有标签。"""
    response = requests.get(f"{BASE_URL}/labels/")
    return response.json()


def demo_search_operations():
    """演示搜索操作。"""
    print_section("搜索操作")
    
    # 按文本内容搜索
    print("1. 搜索包含 'refund' 的文本:")
    results = search_annotations(query="refund", per_page=3)
    print(f"找到 {results['total']} 个文本")
    for item in results['items']:
        print(f"  ID: {item['id']}, 标签: {item['labels']}")
        print(f"  文本: {item['text'][:100]}...")
    
    # 按标签搜索
    print("\n2. 搜索带有 'angry' 标签的文本:")
    results = search_annotations(labels="angry", per_page=3)
    print(f"找到 {results['total']} 个带有 'angry' 标签的文本")
    for item in results['items']:
        print(f"  ID: {item['id']}, 文本: {item['text'][:80]}...")
    
    # 搜索未标注文本（导入后应该没有）
    print("\n3. 搜索未标注文本:")
    results = search_annotations(unlabeled_only=True, per_page=5)
    print(f"找到 {results['total']} 个未标注文本")


def demo_create_and_label():
    """演示创建新标注和标注操作。"""
    print_section("创建和标注操作")
    
    # 导入一些新的未标注文本
    new_texts = [
        "你好，我需要帮助处理我的订单",
        "我的包裹什么时候到达？",
        "我想退回这个产品",
        "物品损坏了，请发送替换品",
        "谢谢你们快速的运输！"
    ]
    
    print("1. 导入新的未标注文本:")
    result = import_texts(new_texts)
    print(f"导入了 {result['imported_count']} 个新文本")
    
    # 搜索未标注文本
    print("\n2. 查找新导入的未标注文本:")
    results = search_annotations(unlabeled_only=True, per_page=10)
    print(f"找到 {results['total']} 个未标注文本")
    
    if results['items']:
        # 获取前几个未标注文本的 ID
        text_ids = [item['id'] for item in results['items'][:3]]
        
        print(f"\n3. 批量标注 ID 为 {text_ids} 的文本:")
        bulk_result = bulk_label(text_ids, "customer_service,inquiry")
        print(f"更新了 {bulk_result['updated_count']} 个文本")
        
        # 验证标注
        print("\n4. 验证标签是否已应用:")
        for text_id in text_ids:
            response = requests.get(f"{BASE_URL}/annotations/{text_id}")
            if response.status_code == 200:
                item = response.json()
                print(f"  ID: {item['id']}, 标签: {item['labels']}")
                print(f"  文本: {item['text'][:60]}...")


def demo_statistics():
    """演示统计操作。"""
    print_section("统计信息")
    
    stats = get_system_stats()
    print(f"总文本数: {stats['total_texts']:,}")
    print(f"已标注文本: {stats['labeled_texts']:,}")
    print(f"未标注文本: {stats['unlabeled_texts']:,}")
    print(f"总唯一标签数: {stats['total_labels']}")
    
    print(f"\n前10个最常见的标签:")
    for i, label_stat in enumerate(stats['label_statistics'][:10], 1):
        print(f"  {i:2d}. {label_stat['label']}: {label_stat['count']:,} 个文本")


def demo_label_management():
    """演示标签管理。"""
    print_section("标签管理")
    
    labels = get_all_labels()
    print(f"系统中的标签总数: {len(labels)}")
    
    print("\n标签样例:")
    for label in labels[:10]:
        print(f"  ID: {label['id']:3d}, 标签: {label['label']}")


def main():
    """主演示函数。"""
    print("文本标注系统 - API 演示")
    print("确保服务器在 http://localhost:8000 运行")
    
    try:
        # 测试服务器连接
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("错误: 服务器无响应!")
            return
        
        print("✓ 服务器正在运行")
        
        # 运行演示
        demo_statistics()
        demo_label_management()
        demo_search_operations()
        demo_create_and_label()
        
        # 最终统计
        demo_statistics()
        
        print_section("演示完成")
        print("API 演示已成功完成!")
        print("你可以在以下地址探索更多端点: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器! 请确保服务器在 http://localhost:8000 运行")
    except Exception as e:
        print(f"演示过程中发生错误: {e}")


if __name__ == "__main__":
    main() 