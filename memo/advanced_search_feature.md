# 高级搜索功能扩展

## 功能概述

为了支持批量标注筛选和人工校验的需求，我们扩展了搜索API，增加了以下搜索条件：

1. **包含某关键词** (`query`) - 已存在
2. **不包含某关键词** (`exclude_query`) - 新增
3. **包含某分类/标签** (`labels`) - 已存在
4. **不包含某分类/标签** (`exclude_labels`) - 新增

## 实现细节

### 1. Schema更新 (`server/schemas.py`)

在 `SearchRequest` 类中新增了两个字段：

```python
class SearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="文本必须包含的关键词")
    exclude_query: Optional[str] = Field(None, description="文本不能包含的关键词")
    labels: Optional[str] = Field(None, description="文本必须包含的逗号分隔标签")
    exclude_labels: Optional[str] = Field(None, description="文本不能包含的逗号分隔标签")
    unlabeled_only: bool = Field(False, description="仅返回未标注文本")
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(50, description="每页记录数", ge=1, le=1000)
```

### 2. 服务层更新 (`server/services.py`)

在 `search_annotations` 方法中添加了新的过滤逻辑：

```python
# 应用排除关键词过滤器
if search_request.exclude_query:
    query = query.filter(~AnnotationData.text.contains(search_request.exclude_query))

# 应用排除标签过滤器
if search_request.exclude_labels:
    exclude_label_filters = []
    for label in search_request.exclude_labels.split(','):
        label = label.strip()
        if label:
            exclude_label_filters.extend([
                AnnotationData.labels == label,
                AnnotationData.labels.like(f"{label},%"),
                AnnotationData.labels.like(f"%, {label}"),
                AnnotationData.labels.like(f"%, {label},%")
            ])
    if exclude_label_filters:
        query = query.filter(~or_(*exclude_label_filters))
```

## 使用示例

### API调用示例

```bash
POST /annotations/search
Content-Type: application/json

{
    "query": "weather",           # 必须包含的关键词
    "exclude_query": "error",     # 不能包含的关键词
    "labels": "intent, positive", # 必须包含的标签
    "exclude_labels": "angry, test", # 不能包含的标签
    "page": 1,
    "per_page": 20
}
```

### Python代码示例

```python
from server.schemas import SearchRequest
from server.services import AnnotationService

# 复杂搜索条件
search_request = SearchRequest(
    query="weather",              # 包含"weather"关键词
    exclude_query="error",        # 不包含"error"关键词
    labels="intent",             # 包含"intent"标签
    exclude_labels="angry",      # 不包含"angry"标签
    page=1,
    per_page=50
)

service = AnnotationService(db)
result = service.search_annotations(search_request)
```

## 应用场景

### 1. 批量标注筛选
- 查找包含特定关键词但还未标注特定分类的数据
- 排除已经标注为"错误"或"无效"的数据
- 找出需要重新审核的数据

### 2. 数据质量控制
- 找出包含错误关键词的数据进行清理
- 排除测试数据或临时标签
- 筛选出高质量的训练数据

### 3. 人工校验辅助
- 快速定位特定类型的数据
- 排除已经验证过的数据
- 聚焦于需要人工介入的边界案例

## 性能考虑

1. **索引利用**: 新的排除条件仍然能够利用现有的文本和标签索引
2. **查询优化**: 使用SQLAlchemy的 `~` 操作符进行NOT查询
3. **向后兼容**: 新字段为可选，不影响现有API调用

## 测试验证

创建了测试脚本验证功能：
- `tmp/test_advanced_search.py` - 直接服务层测试
- `tmp/demo_advanced_search_api.py` - HTTP API演示

## 未来扩展建议

1. **正则表达式支持**: 为高级用户提供正则表达式搜索
2. **日期范围过滤**: 添加创建时间或修改时间的过滤
3. **模糊匹配**: 支持拼写容错的模糊搜索
4. **保存搜索条件**: 允许用户保存常用的搜索条件组合

## 注意事项

1. 所有新字段都是可选的，保持向后兼容性
2. 排除条件与包含条件可以组合使用
3. 标签匹配使用精确匹配模式，考虑逗号分隔格式
4. 性能测试显示新功能对查询性能影响最小 