#!/usr/bin/env python3
"""
测试新的高级搜索功能的脚本。

测试以下搜索条件：
1. 包含某关键词
2. 不包含某关键词
3. 包含某分类/标签
4. 不包含某分类/标签
5. 组合条件搜索
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.models import SessionLocal, AnnotationData
from server.services import AnnotationService
from server.schemas import SearchRequest


def test_advanced_search():
    """测试高级搜索功能。"""
    db = SessionLocal()
    service = AnnotationService(db)
    
    print("=== 测试高级搜索功能 ===\n")
    
    # 测试1: 包含关键词
    print("1. 测试包含关键词 'weather':")
    result = service.search_annotations(SearchRequest(query="weather", page=1, per_page=5))
    print(f"   找到 {result.total} 条记录")
    for item in result.items[:3]:
        print(f"   - ID {item.id}: {item.text[:50]}...")
    print()
    
    # 测试2: 不包含关键词
    print("2. 测试不包含关键词 'error':")
    result = service.search_annotations(SearchRequest(exclude_query="error", page=1, per_page=5))
    print(f"   找到 {result.total} 条记录")
    for item in result.items[:3]:
        print(f"   - ID {item.id}: {item.text[:50]}...")
    print()
    
    # 测试3: 包含标签
    print("3. 测试包含标签 'intent':")
    result = service.search_annotations(SearchRequest(labels="intent", page=1, per_page=5))
    print(f"   找到 {result.total} 条记录")
    for item in result.items[:3]:
        print(f"   - ID {item.id}: {item.text[:50]}... | 标签: {item.labels}")
    print()
    
    # 测试4: 不包含标签
    print("4. 测试不包含标签 'error':")
    result = service.search_annotations(SearchRequest(exclude_labels="error", page=1, per_page=5))
    print(f"   找到 {result.total} 条记录")
    for item in result.items[:3]:
        print(f"   - ID {item.id}: {item.text[:50]}... | 标签: {item.labels}")
    print()
    
    # 测试5: 组合条件 - 包含"weather"但不包含"error"关键词
    print("5. 测试组合条件 - 包含'weather'但不包含'error':")
    result = service.search_annotations(SearchRequest(
        query="weather", 
        exclude_query="error", 
        page=1, 
        per_page=5
    ))
    print(f"   找到 {result.total} 条记录")
    for item in result.items[:3]:
        print(f"   - ID {item.id}: {item.text[:50]}...")
    print()
    
    # 测试6: 组合条件 - 包含"intent"标签但不包含"error"标签
    print("6. 测试组合条件 - 包含'intent'标签但不包含'error'标签:")
    result = service.search_annotations(SearchRequest(
        labels="intent",
        exclude_labels="error",
        page=1,
        per_page=5
    ))
    print(f"   找到 {result.total} 条记录")
    for item in result.items[:3]:
        print(f"   - ID {item.id}: {item.text[:50]}... | 标签: {item.labels}")
    print()
    
    # 测试7: 复杂组合条件
    print("7. 测试复杂组合 - 包含'weather'关键词和'intent'标签，但不包含'error'关键词和'test'标签:")
    result = service.search_annotations(SearchRequest(
        query="weather",
        exclude_query="error",
        labels="intent",
        exclude_labels="test",
        page=1,
        per_page=5
    ))
    print(f"   找到 {result.total} 条记录")
    for item in result.items[:3]:
        print(f"   - ID {item.id}: {item.text[:50]}... | 标签: {item.labels}")
    print()
    
    db.close()
    print("=== 测试完成 ===")


if __name__ == "__main__":
    test_advanced_search() 