#!/usr/bin/env python3
"""
更新标签描述脚本

从 label-desc.txt 文件读取数据，更新数据库中已存在的标签的描述。
- 奇数行：中文描述 (description)
- 偶数行：英文标签 (label)
- 只有当 label 在数据库中存在时，才更新其描述
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from server.models import engine, Label
from server.config import DATABASE_URL

def read_and_parse_data(file_path: str) -> list[tuple[str, str]]:
    """
    读取并解析数据文件
    
    Args:
        file_path: 数据文件路径
        
    Returns:
        list[tuple[str, str]]: [(description, label), ...] 的列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 去除空行和去除首尾空白字符
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    # 确保行数是偶数（每个标签都有对应的描述）
    if len(non_empty_lines) % 2 != 0:
        print(f"警告: 行数不是偶数，最后一行将被忽略。总行数: {len(non_empty_lines)}")
        non_empty_lines = non_empty_lines[:-1]
    
    # 配对：奇数行（索引0,2,4...）是描述，偶数行（索引1,3,5...）是标签
    pairs = []
    for i in range(0, len(non_empty_lines), 2):
        description = non_empty_lines[i]  # 奇数行（中文描述）
        label = non_empty_lines[i + 1]    # 偶数行（英文标签）
        pairs.append((description, label))
    
    return pairs

def update_label_descriptions(pairs: list[tuple[str, str]]) -> dict:
    """
    更新数据库中已存在标签的描述
    
    Args:
        pairs: [(description, label), ...] 的列表
        
    Returns:
        dict: 包含统计信息的字典
    """
    stats = {
        'total_pairs': len(pairs),
        'updated': 0,
        'not_found': 0,
        'errors': 0,
        'not_found_labels': [],
        'updated_labels': []
    }
    
    with Session(engine) as session:
        for description, label in pairs:
            try:
                # 查找是否存在该标签
                existing_label = session.query(Label).filter(Label.label == label).first()
                
                if existing_label:
                    # 更新描述
                    existing_label.description = description
                    stats['updated'] += 1
                    stats['updated_labels'].append(label)
                    print(f"✓ 更新标签 '{label}' 的描述: '{description}'")
                else:
                    stats['not_found'] += 1
                    stats['not_found_labels'].append(label)
                    print(f"⚠ 标签 '{label}' 在数据库中不存在，跳过")
                    
            except Exception as e:
                stats['errors'] += 1
                print(f"✗ 处理标签 '{label}' 时出错: {e}")
        
        try:
            # 提交所有更改
            session.commit()
            print(f"\n✓ 成功提交所有更改到数据库")
        except Exception as e:
            session.rollback()
            print(f"✗ 提交更改失败: {e}")
            stats['errors'] = stats['total_pairs']
            stats['updated'] = 0
    
    return stats

def main():
    """主函数"""
    # 数据文件路径
    data_file = Path(__file__).parent / "label-desc.txt"
    
    if not data_file.exists():
        print(f"错误: 数据文件 {data_file} 不存在")
        return 1
    
    print(f"开始处理数据文件: {data_file}")
    print(f"数据库: {DATABASE_URL}")
    print("-" * 50)
    
    try:
        # 读取和解析数据
        pairs = read_and_parse_data(str(data_file))
        print(f"解析到 {len(pairs)} 个标签-描述对")
        
        # 更新数据库
        stats = update_label_descriptions(pairs)
        
        # 输出统计信息
        print("\n" + "=" * 50)
        print("处理结果统计:")
        print(f"总计处理: {stats['total_pairs']} 个标签")
        print(f"成功更新: {stats['updated']} 个")
        print(f"未找到: {stats['not_found']} 个")
        print(f"出错: {stats['errors']} 个")
        
        if stats['not_found_labels']:
            print(f"\n未找到的标签列表:")
            for label in stats['not_found_labels']:
                print(f"  - {label}")
        
        if stats['updated_labels']:
            print(f"\n成功更新的标签:")
            for label in stats['updated_labels']:
                print(f"  + {label}")
        
        return 0 if stats['errors'] == 0 else 1
        
    except Exception as e:
        print(f"脚本执行失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 