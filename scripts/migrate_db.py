"""
数据库迁移脚本

为现有数据库添加索引以提高查询性能。
特别针对11万+数据量的性能优化。
"""

import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from server.config import DATABASE_URL


def migrate_database():
    """迁移数据库，添加性能优化的索引"""
    
    # 解析数据库文件路径
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = project_root / db_path[2:]
    
    print(f"正在迁移数据库: {db_path}")
    
    # 检查数据库文件是否存在
    if not Path(db_path).exists():
        print("数据库文件不存在，请先运行数据导入。")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查现有索引
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='annotation_data'")
        existing_indexes = [row[0] for row in cursor.fetchall()]
        print(f"现有索引: {existing_indexes}")
        
        # 添加索引（如果不存在）
        indexes_to_add = [
            ("ix_annotation_data_text", "CREATE INDEX IF NOT EXISTS ix_annotation_data_text ON annotation_data (text)"),
            ("ix_annotation_data_labels", "CREATE INDEX IF NOT EXISTS ix_annotation_data_labels ON annotation_data (labels)"),
            ("ix_text_labels", "CREATE INDEX IF NOT EXISTS ix_text_labels ON annotation_data (text, labels)"),
            ("ix_labels_partial", "CREATE INDEX IF NOT EXISTS ix_labels_partial ON annotation_data (labels)"),
            ("ix_labels_label", "CREATE INDEX IF NOT EXISTS ix_labels_label ON labels (label)"),
        ]
        
        for index_name, sql in indexes_to_add:
            if index_name not in existing_indexes:
                print(f"正在创建索引: {index_name}")
                cursor.execute(sql)
            else:
                print(f"索引已存在: {index_name}")
        
        # 优化数据库
        print("正在执行数据库优化...")
        cursor.execute("ANALYZE")  # 更新查询优化器统计信息
        cursor.execute("VACUUM")   # 重新组织数据库文件
        
        conn.commit()
        print("数据库迁移完成！")
        
        # 显示迁移后的信息
        cursor.execute("SELECT COUNT(*) FROM annotation_data")
        annotation_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM labels")
        label_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='annotation_data'")
        final_indexes = [row[0] for row in cursor.fetchall()]
        
        print(f"\n迁移结果:")
        print(f"- 标注数据: {annotation_count:,} 条")
        print(f"- 标签数量: {label_count} 个")
        print(f"- 索引数量: {len(final_indexes)} 个")
        print(f"- 索引列表: {', '.join(final_indexes)}")
        
        return True
        
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def test_query_performance():
    """测试查询性能"""
    
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = project_root / db_path[2:]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    import time
    
    try:
        print("\n性能测试:")
        
        # 测试文本搜索
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM annotation_data WHERE text LIKE '%测试%'")
        result = cursor.fetchone()[0]
        text_search_time = time.time() - start_time
        print(f"- 文本搜索 (LIKE): {text_search_time:.3f}秒, 结果: {result} 条")
        
        # 测试标签搜索
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM annotation_data WHERE labels LIKE '%label%'")
        result = cursor.fetchone()[0]
        label_search_time = time.time() - start_time
        print(f"- 标签搜索 (LIKE): {label_search_time:.3f}秒, 结果: {result} 条")
        
        # 测试复合查询
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM annotation_data WHERE text LIKE '%' AND labels LIKE '%label%'")
        result = cursor.fetchone()[0]
        compound_search_time = time.time() - start_time
        print(f"- 复合查询: {compound_search_time:.3f}秒, 结果: {result} 条")
        
        # 测试分页查询
        start_time = time.time()
        cursor.execute("SELECT id, text, labels FROM annotation_data LIMIT 50 OFFSET 1000")
        results = cursor.fetchall()
        pagination_time = time.time() - start_time
        print(f"- 分页查询 (LIMIT 50 OFFSET 1000): {pagination_time:.3f}秒, 结果: {len(results)} 条")
        
    except Exception as e:
        print(f"性能测试失败: {e}")
    finally:
        conn.close()


def main():
    """主函数，用于命令行调用"""
    print("开始数据库优化迁移...")
    success = migrate_database()
    
    if success:
        print("\n测试查询性能...")
        test_query_performance()
        
        print("\n迁移完成！数据库已优化。")
        print("提示：服务器将在下次启动时自动使用优化后的索引。")
    else:
        print("迁移失败，请检查错误信息。")


if __name__ == "__main__":
    main() 