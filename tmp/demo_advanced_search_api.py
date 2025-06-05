#!/usr/bin/env python3
"""
演示通过HTTP API使用新的高级搜索功能。

这个脚本展示如何通过REST API调用新的搜索条件：
1. 包含某关键词 (query)
2. 不包含某关键词 (exclude_query)
3. 包含某分类/标签 (labels)
4. 不包含某分类/标签 (exclude_labels)
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def search_annotations(**kwargs):
    """通用搜索函数。"""
    url = f"{BASE_URL}/annotations/search"
    response = requests.post(url, json=kwargs)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"错误: {response.status_code} - {response.text}")
        return None


def demo_advanced_search():
    """演示高级搜索API功能。"""
    print("=== 高级搜索API演示 ===\n")
    
    # 示例1: 基本包含搜索
    print("1. 搜索包含'weather'的文本:")
    result = search_annotations(query="weather", page=1, per_page=3)
    if result:
        print(f"   找到 {result['total']} 条记录")
        for item in result['items']:
            print(f"   - ID {item['id']}: {item['text'][:50]}...")
    print()
    
    # 示例2: 排除关键词搜索
    print("2. 搜索不包含'error'的文本:")
    result = search_annotations(exclude_query="error", page=1, per_page=3)
    if result:
        print(f"   找到 {result['total']} 条记录")
        for item in result['items']:
            print(f"   - ID {item['id']}: {item['text'][:50]}...")
    print()
    
    # 示例3: 包含特定标签
    print("3. 搜索包含'angry'标签的文本:")
    result = search_annotations(labels="angry", page=1, per_page=3)
    if result:
        print(f"   找到 {result['total']} 条记录")
        for item in result['items']:
            print(f"   - ID {item['id']}: {item['text'][:50]}... | 标签: {item['labels']}")
    print()
    
    # 示例4: 排除特定标签
    print("4. 搜索不包含'angry'标签的文本:")
    result = search_annotations(exclude_labels="angry", page=1, per_page=3)
    if result:
        print(f"   找到 {result['total']} 条记录")
        for item in result['items']:
            print(f"   - ID {item['id']}: {item['text'][:50]}... | 标签: {item['labels']}")
    print()
    
    # 示例5: 组合条件 - 包含关键词但排除另一关键词
    print("5. 搜索包含'weather'但不包含'error'的文本:")
    result = search_annotations(
        query="weather",
        exclude_query="error",
        page=1,
        per_page=3
    )
    if result:
        print(f"   找到 {result['total']} 条记录")
        for item in result['items']:
            print(f"   - ID {item['id']}: {item['text'][:50]}...")
    print()
    
    # 示例6: 复杂组合搜索
    print("6. 复杂搜索 - 包含'weather'关键词，包含'happy'标签，但不包含'error'关键词:")
    result = search_annotations(
        query="weather",
        exclude_query="error",
        labels="happy",
        page=1,
        per_page=3
    )
    if result:
        print(f"   找到 {result['total']} 条记录")
        for item in result['items']:
            print(f"   - ID {item['id']}: {item['text'][:50]}... | 标签: {item['labels']}")
    print()
    
    # 示例7: 显示API请求示例
    print("7. API请求示例:")
    api_example = {
        "query": "weather",           # 必须包含的关键词
        "exclude_query": "error",     # 不能包含的关键词
        "labels": "happy, positive",  # 必须包含的标签
        "exclude_labels": "angry, negative",  # 不能包含的标签
        "unlabeled_only": False,      # 是否只返回未标注的
        "page": 1,
        "per_page": 20
    }
    
    print("   POST /annotations/search")
    print("   Content-Type: application/json")
    print("   Request Body:")
    print(json.dumps(api_example, indent=4, ensure_ascii=False))
    print()
    
    print("=== 演示完成 ===")


if __name__ == "__main__":
    demo_advanced_search() 