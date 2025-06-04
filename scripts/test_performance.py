"""
性能测试脚本

测试数据库优化后的API性能，特别是搜索和查询功能。
"""

import requests
import time
from typing import Dict, List
import json


def test_api_performance(base_url: str = "http://localhost:8000") -> None:
    """测试API性能"""
    
    print("=== API性能测试 ===")
    print(f"测试服务器: {base_url}")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ 服务器连接正常")
        else:
            print("❌ 服务器连接失败")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return
    
    # 定义测试用例
    test_cases = [
        {
            "name": "获取系统统计",
            "method": "GET",
            "url": "/stats",
            "expected_time": 1.0  # 期望1秒内完成
        },
        {
            "name": "分页查询（前50条）",
            "method": "POST",
            "url": "/annotations/search",
            "data": {"query": "", "page": 1, "per_page": 50},
            "expected_time": 0.5
        },
        {
            "name": "分页查询（中间页）",
            "method": "POST",
            "url": "/annotations/search",
            "data": {"query": "", "page": 100, "per_page": 50},
            "expected_time": 0.5
        },
        {
            "name": "文本搜索（通用关键词）",
            "method": "POST",
            "url": "/annotations/search",
            "data": {"query": "the", "page": 1, "per_page": 20},
            "expected_time": 1.0
        },
        {
            "name": "标签搜索",
            "method": "POST",
            "url": "/annotations/search",
            "data": {"labels": "intent", "page": 1, "per_page": 20},
            "expected_time": 1.0
        },
        {
            "name": "复合搜索",
            "method": "POST",
            "url": "/annotations/search",
            "data": {"query": "weather", "labels": "intent", "page": 1, "per_page": 20},
            "expected_time": 1.5
        },
        {
            "name": "未标注数据查询",
            "method": "POST",
            "url": "/annotations/search",
            "data": {"unlabeled_only": True, "page": 1, "per_page": 20},
            "expected_time": 1.0
        },
        {
            "name": "大页面查询",
            "method": "POST",
            "url": "/annotations/search",
            "data": {"query": "", "page": 1, "per_page": 200},
            "expected_time": 1.0
        }
    ]
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}] 测试: {test_case['name']}")
        
        start_time = time.time()
        
        try:
            if test_case["method"] == "GET":
                response = requests.get(f"{base_url}{test_case['url']}")
            else:
                response = requests.post(
                    f"{base_url}{test_case['url']}",
                    json=test_case.get("data", {})
                )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # 提取有用信息
                info = {}
                if "total" in response_data:
                    info["total"] = response_data["total"]
                if "items" in response_data and isinstance(response_data["items"], list):
                    info["returned"] = len(response_data["items"])
                
                # 判断是否通过
                passed = execution_time <= test_case["expected_time"]
                status = "✅ 通过" if passed else "⚠️  较慢"
                
                if passed:
                    passed_tests += 1
                
                print(f"  响应时间: {execution_time:.3f}秒 (期望: ≤{test_case['expected_time']}秒)")
                print(f"  状态: {status}")
                if info:
                    print(f"  数据: {info}")
                
                results.append({
                    "test": test_case["name"],
                    "time": execution_time,
                    "expected": test_case["expected_time"],
                    "passed": passed,
                    "info": info
                })
                
            else:
                print(f"  ❌ 错误: HTTP {response.status_code}")
                print(f"  响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    # 性能总结
    print(f"\n=== 性能测试总结 ===")
    print(f"总测试数: {total_tests}")
    print(f"通过数: {passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    # 按性能排序
    results.sort(key=lambda x: x["time"])
    
    print("\n最快的5个操作:")
    for result in results[:5]:
        print(f"  {result['test']}: {result['time']:.3f}秒")
    
    if len(results) > 5:
        print("\n最慢的3个操作:")
        for result in results[-3:]:
            status = "正常" if result["passed"] else "需优化"
            print(f"  {result['test']}: {result['time']:.3f}秒 ({status})")
    
    # 保存详细结果
    with open("performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "pass_rate": passed_tests/total_tests*100
            },
            "details": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: performance_test_results.json")


def test_database_queries() -> None:
    """直接测试数据库查询性能"""
    
    print("\n=== 数据库查询性能测试 ===")
    
    import sys
    from pathlib import Path
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    
    from app.models import SessionLocal, AnnotationData, Label
    from app.services import AnnotationService, StatisticsService
    from app.schemas import SearchRequest
    
    db = SessionLocal()
    annotation_service = AnnotationService(db)
    stats_service = StatisticsService(db)
    
    try:
        # 测试各种查询
        queries = [
            {
                "name": "统计查询",
                "func": lambda: stats_service.get_system_stats(),
                "expected_time": 1.0
            },
            {
                "name": "简单分页",
                "func": lambda: annotation_service.search_annotations(
                    SearchRequest(query="", page=1, per_page=50)
                ),
                "expected_time": 0.3
            },
            {
                "name": "文本搜索",
                "func": lambda: annotation_service.search_annotations(
                    SearchRequest(query="weather", page=1, per_page=20)
                ),
                "expected_time": 0.5
            },
            {
                "name": "标签搜索",
                "func": lambda: annotation_service.search_annotations(
                    SearchRequest(labels="intent", page=1, per_page=20)
                ),
                "expected_time": 0.5
            },
            {
                "name": "复合搜索",
                "func": lambda: annotation_service.search_annotations(
                    SearchRequest(query="weather", labels="intent", page=1, per_page=20)
                ),
                "expected_time": 0.8
            }
        ]
        
        for query in queries:
            start_time = time.time()
            result = query["func"]()
            end_time = time.time()
            execution_time = end_time - start_time
            
            passed = execution_time <= query["expected_time"]
            status = "✅ 通过" if passed else "⚠️  较慢"
            
            print(f"{query['name']}: {execution_time:.3f}秒 {status}")
            
            # 显示结果信息
            if hasattr(result, 'total'):
                print(f"  结果数量: {result.total}")
            elif hasattr(result, 'total_texts'):
                print(f"  总文本: {result.total_texts}, 已标注: {result.labeled_texts}")
    
    finally:
        db.close()


def main():
    """主函数"""
    print("开始性能测试...")
    
    # 测试API性能
    test_api_performance()
    
    # 测试数据库查询性能
    test_database_queries()
    
    print("\n性能测试完成！")


if __name__ == "__main__":
    main()