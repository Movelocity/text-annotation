"""
测试'thanksWishes'标签验证功能的简单脚本。

用于快速测试验证功能是否正常工作。
"""

import sys
import os
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API基础URL
BASE_URL = "http://localhost:8000"


def test_server_health():
    """测试服务器健康状态。"""
    print("🔍 测试服务器健康状态...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("  ✅ 服务器正常")
            return True
        else:
            print(f"  ❌ 服务器异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        return False


def test_single_text_check():
    """测试单个文本检查功能。"""
    print("\n🔍 测试单个文本检查功能...")
    
    test_cases = [
        {
            "text": "谢谢您的帮助，非常感谢！",
            "label": "thanksWishes"
        },
        {
            "text": "祝您新年快乐，万事如意！",
            "label": "thanksWishes"
        },
        {
            "text": "我想查询我的订单状态",
            "label": "thanksWishes"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"  文本: {test_case['text']}")
        print(f"  标签: {test_case['label']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/verify/check-text",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 检查结果: {result['is_correct']}")
                print(f"     消息: {result['message']}")
            else:
                print(f"  ❌ 检查失败: {response.status_code}")
                print(f"     错误信息: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")


def test_create_verification_batch():
    """测试创建验证批次。"""
    print("\n🔍 测试创建验证批次...")
    
    request_data = {
        "target_label": "thanksWishes"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/verify/label",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ 成功创建验证批次")
            print(f"     批次ID: {result['batch_id']}")
            print(f"     目标标签: {result['target_label']}")
            print(f"     总任务数: {result['total_tasks']}")
            print(f"     消息: {result['message']}")
            
            return result['batch_id']
        else:
            print(f"  ❌ 创建失败: {response.status_code}")
            print(f"     错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
        return None


def test_get_batch_progress(batch_id):
    """测试获取批次进度。"""
    if not batch_id:
        print("\n⚠️  跳过进度测试（无批次ID）")
        return
    
    print(f"\n🔍 测试获取批次进度 (批次ID: {batch_id})...")
    
    try:
        response = requests.get(f"{BASE_URL}/verify/batch/{batch_id}/progress")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ 成功获取进度")
            print(f"     批次ID: {result['batch_id']}")
            print(f"     目标标签: {result['target_label']}")
            print(f"     总任务数: {result['total_tasks']}")
            print(f"     完成任务数: {result['completed_tasks']}")
            print(f"     状态: {result['status']}")
            print(f"     完成百分比: {result['progress_percentage']:.1f}%")
        else:
            print(f"  ❌ 获取进度失败: {response.status_code}")
            print(f"     错误信息: {response.text}")
            
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")


def main():
    """主测试函数。"""
    print("🚀 开始'thanksWishes'标签验证功能测试")
    print("=" * 50)
    
    # 1. 测试服务器健康状态
    if not test_server_health():
        print("\n❌ 服务器不可用，请先启动服务器")
        return
    
    # 2. 测试单个文本检查
    test_single_text_check()
    
    # 3. 测试创建验证批次
    batch_id = test_create_verification_batch()
    
    # 4. 测试获取批次进度
    test_get_batch_progress(batch_id)
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("\n💡 提示：")
    print("   - 如果所有测试都通过，说明验证功能正常工作")
    print("   - 可以运行 scripts/verify_thanks_wishes.py 进行完整的验证流程")
    print("   - 单个文本检查功能可以用于快速验证标签的正确性")


if __name__ == "__main__":
    main() 