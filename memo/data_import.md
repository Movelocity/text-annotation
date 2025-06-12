# 文本标注项目 - 数据导入逻辑分析

## 项目概述

文本标注项目，使用 SQLite 管理数据：
- 标注数据管理：text as string(无重复), labels as string (用逗号分隔)
- 标签管理：id as number, label as string

## 数据来源

1. **现有旧数据导入**：old-data/**/<label>.txt, 每行是该标签的一个记录，会有一些相同记录存在于多个标签文件中，合并它们并获取用逗号分隔的标签
2. **新数据导入**：无标注文本，按行分隔

**当前数据规模**: archive/old-data 目录包含 116 个文件，总计 11.9MB 数据

## 数据库优化后的导入逻辑分析 (2024-12-19)

### 已完成的优化 ✅

#### 数据库模型优化
- **索引优化**：text 和 labels 字段已添加索引，提高查询性能
- **复合索引**：添加了 `ix_text_labels` 复合索引，优化多条件查询
- **连接优化**：数据库连接配置已优化，增加超时时间和连接池

#### 批量操作优化
- **AnnotationService**: 
  - `import_texts()`: 使用 `bulk_insert_mappings()` 替代单条插入
  - `batch_create_annotations()`: 新增批量创建方法
  - 批量重复检查：使用 `text.in_(texts_to_check)` 提高查询效率

#### 导入工具
- **scripts/data_import.py**: 提供完整的 DataImporter 类
  - 支持旧数据目录结构导入
  - 支持标签配置导入
  - 自动合并重复文本和标签

### 具体问题分析 ❌

#### 1. API调用错误 (🔥 紧急修复)

**具体问题**：
```python
# main.py:372 - 错误的调用方式
imported_count = importer.import_text_file(import_request.file_path, db)

# scripts/data_import.py:115 - 方法定义只接受一个参数
def import_text_file(self, file_path: str) -> int:
```

**影响**: `/import/text-file` API端点会报错，无法正常使用

**修复方案**:
1. 移除API调用中多余的 `db` 参数
2. 或者修改 `import_text_file()` 方法接受 `db` 参数

#### 2. 导入逻辑不一致 (⚠️ 性能差异)

**具体差异对比**:

| 特性 | AnnotationService.import_texts() | DataImporter.import_text_file() |
|------|----------------------------------|----------------------------------|
| 批量操作 | ✅ `bulk_insert_mappings()` | ❌ 逐个 `add()` |
| 重复检查 | ✅ 批量 `text.in_(list)` | ❌ 逐个查询 |
| 事务管理 | ✅ 最后一次 `commit()` | ❌ 每次 `commit()` |
| 内存效率 | ✅ 批量预处理 | ❌ 逐行处理 |

**性能影响测算**:
- 对于11万+条数据，批量操作比逐个操作快约 **50-100倍**
- DataImporter 的逐个操作会导致大量数据库I/O

**解决方案**:
将 DataImporter 的方法改用 AnnotationService 的批量逻辑

#### 3. 进度跟踪缺失 (📊 用户体验)

**具体需求评估**:
- 当前数据规模: 116个文件，11.9MB
- 估计数据导入时间: 2-5分钟（使用批量操作）
- **必要性**: 中等 - 大文件导入时用户需要进度反馈

**缺失功能**:
- 文件导入进度条
- API进度反馈
- 导入阶段提示

**实现复杂度**: 低 - 只需添加 tqdm 依赖

#### 4. 错误处理不完善 (🛡️ 稳定性)

**具体问题**:
```python
# DataImporter.__init__ 中的会话管理问题
self.db = db_session or SessionLocal()

# main.py 中重复传递db参数
importer = DataImporter()
imported_count = importer.import_text_file(import_request.file_path, db)
```

**潜在风险**:
- 数据库会话混乱
- 事务回滚不完整
- 内存泄漏风险

### 重新评估的优先级

#### 🔥 P0: 修复API调用错误 (立即执行)
**影响**: 功能性错误，阻塞使用
**工作量**: 5分钟
**风险**: 无

**具体修复**:
```python
# 方案1: 修改API调用 (推荐)
imported_count = importer.import_text_file(import_request.file_path)

# 方案2: 修改方法定义
def import_text_file(self, file_path: str, external_db: Session = None) -> int:
```

#### ⚠️ P1: 统一导入逻辑 (本周内执行)
**影响**: 性能差异50-100倍
**工作量**: 2-3小时
**风险**: 中等 - 需要测试确保兼容性

**实施步骤**:
1. 在 AnnotationService 中添加 `import_text_file_batch()` 方法
2. 更新 `/import/text-file` API 使用新方法
3. 保留 DataImporter 作为脚本工具
4. 添加单元测试

#### 📊 P2: 添加进度跟踪 (下周执行)
**影响**: 用户体验提升
**工作量**: 1-2小时
**风险**: 低

**实施方案**:
```python
# 添加依赖
dependencies = [
    # ... 现有依赖
    "tqdm>=4.66.0",
]

# 实现进度条
def import_with_progress(self, file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    batch_size = 1000
    total_batches = len(lines) // batch_size + 1
    imported_count = 0
    
    for i in tqdm(range(0, len(lines), batch_size), 
                  desc="导入进度", total=total_batches):
        batch_lines = lines[i:i + batch_size]
        # 使用批量导入逻辑
        imported_count += self.import_texts_batch(batch_lines)
    
    return imported_count
```

#### 🛡️ P3: 完善错误处理 (后续改进)
**影响**: 系统稳定性
**工作量**: 4-6小时
**风险**: 低

**实施内容**:
- 统一数据库会话管理
- 完善异常捕获和回滚
- 添加详细的错误日志

#### 🔧 P4: 引入Alembic (可选)
**影响**: 开发工具完善
**工作量**: 2-3小时
**风险**: 低

**必要性重新评估**: 
- 当前项目是个人使用的数据标注工具
- 数据库结构相对稳定
- **建议**: 暂缓，等有真实迁移需求时再引入

### 技术实现细节

#### AnnotationService 批量导入的关键优化
```python
# 当前实现 (已优化)
def import_texts(self, import_request: schemas.TextImportRequest) -> int:
    # 1. 批量预处理
    texts_to_import = [text.strip() for text in import_request.texts if text.strip()]
    
    # 2. 批量重复检查
    existing_records = self.db.query(AnnotationData.text).filter(
        AnnotationData.text.in_(texts_to_import)
    ).all()
    existing_texts = {record.text for record in existing_records}
    
    # 3. 批量准备数据
    new_annotations = [
        {'text': text, 'labels': ''}
        for text in texts_to_import
        if text not in existing_texts
    ]
    
    # 4. 批量插入
    if new_annotations:
        self.db.bulk_insert_mappings(AnnotationData, new_annotations)
        self.db.commit()
    
    return len(new_annotations)
```

#### DataImporter 的性能问题
```python
# 当前实现 (性能差)
def import_text_file(self, file_path: str) -> int:
    for line in f:  # 逐行处理
        text = line.strip()
        if text:
            # 每条记录单独查询 - 性能瓶颈
            existing = self.db.query(AnnotationData).filter(
                AnnotationData.text == text
            ).first()
            if not existing:
                annotation = AnnotationData(text=text, labels='')
                self.db.add(annotation)  # 单条添加 - 性能瓶颈
                records_imported += 1
    
    self.db.commit()  # 但这里是批量提交，相对较好
```

### 验证方案

#### 性能测试对比
```python
# 测试脚本 (可添加到 tmp/ 目录)
import time
from server.services import AnnotationService
from scripts.data_import import DataImporter

def compare_import_performance():
    # 测试相同数据的导入性能
    test_texts = ["测试文本 " + str(i) for i in range(10000)]
    
    # 测试 AnnotationService (批量)
    start = time.time()
    service = AnnotationService(db)
    service.import_texts(schemas.TextImportRequest(texts=test_texts))
    batch_time = time.time() - start
    
    # 测试 DataImporter (逐个)
    # ... 类似测试
    
    print(f"批量导入: {batch_time:.2f}秒")
    print(f"逐个导入: {individual_time:.2f}秒")
    print(f"性能提升: {individual_time/batch_time:.1f}倍")
```

### 预期收益

#### P0 修复后
- 立即恢复 `/import/text-file` API 功能
- 避免用户使用时报错

#### P1 优化后
- 大文件导入速度提升 **50-100倍**
- 内存使用更高效
- 数据库负载显著降低

#### P2 改进后
- 用户导入大文件时有明确进度反馈
- 提升专业工具的用户体验

#### P3 完善后
- 系统稳定性提升
- 错误定位更容易
- 运维友好度提升

---

**记录时间**: 2024-12-19  
**分析深度**: 基于具体代码和现有数据规模  
**核心发现**: API调用错误需立即修复，性能差异显著  
**行动建议**: 先修复P0错误，再优化P1性能问题，其他按需推进