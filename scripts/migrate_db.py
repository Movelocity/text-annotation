"""
数据库迁移脚本。

用于创建和更新数据库表结构。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.models import create_tables, Base, engine
from server.config import DATABASE_URL


def migrate_database():
    """执行数据库迁移。"""
    print("开始数据库迁移...")
    
    try:
        # 创建所有表（包括新添加的验证表）
        create_tables()
        print("✅ 数据库迁移完成")
        
        # 验证表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'annotation_data',
            'labels', 
            'verification_batches',
            'verification_tasks'
        ]
        
        print("\n📋 数据库表列表:")
        for table in expected_tables:
            if table in tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} (未找到)")
        
        print(f"\n总共 {len(tables)} 个表")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    migrate_database() 