#!/usr/bin/env python3
"""
数据导入脚本，用于导入旧的标注数据。

运行此脚本来导入现有的标注数据并设置数据库。
"""

import os
import sys
from data_import import DataImporter, main as import_main
from sqlalchemy.orm import Session
from models import create_tables, get_db
from services import StatisticsService


def main():
    """主导入函数。"""
    print("="*60)
    print("文本标注系统 - 数据导入")
    print("="*60)
    
    # 创建数据库表
    create_tables()
    
    # 执行数据导入
    try:
        print("\n开始执行数据导入流程...")
        import_main()  # 调用 data_import.py 的主函数进行数据导入
        print("数据导入完成！")
    except Exception as e:
        print(f"数据导入过程中出错: {e}")
        print("继续执行统计信息显示...")
    
    print("\n"+"="*60)
    print("导入流程已完成！")
    print("="*60)
    
    # 显示统计信息
    display_statistics()


def display_statistics():
    """显示导入后的统计信息。"""
    try:
        db = next(get_db())
        stats_service = StatisticsService(db)
        stats = stats_service.get_system_stats()
        
        print("\n当前数据库统计信息:")
        print(f"- 总文本数: {stats.total_texts}")
        print(f"- 已标注文本: {stats.labeled_texts}")
        print(f"- 未标注文本: {stats.unlabeled_texts}")
        print(f"- 总唯一标签数: {stats.total_labels}")
        
        if stats.label_statistics:
            print(f"\n前10个最常见的标签:")
            for i, label_stat in enumerate(stats.label_statistics[:10], 1):
                print(f"  {i:2d}. {label_stat.label}: {label_stat.count} 个文本")
        
        db.close()
        
    except Exception as e:
        print(f"获取统计信息时出错: {e}")


def check_data_directory():
    """检查数据目录是否存在并包含必要的文件。"""
    old_data_path = "./archive/old-data"
    if not os.path.exists(old_data_path):
        print(f"警告: 数据目录 {old_data_path} 不存在")
        print("请确保数据目录结构如下:")
        print("""
archive/
└── old-data/
    ├── label_config.yaml
    └── <label_directories>/
        └── *.txt
        """)
        return False
    return True


if __name__ == "__main__":
    if check_data_directory():
        main()
    else:
        print("\n请先创建正确的数据目录结构后再运行此脚本。")
        sys.exit(1) 