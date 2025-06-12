# 关键词数组搜索功能扩展

## 功能概述

为了更好地支持前端高级搜索需求，我们在现有的搜索功能基础上增加了关键词数组搜索功能：

1. **keywords**: 必须包含的关键词数组（精确包含搜索）
2. **exclude_keywords**: 不能包含的关键词数组（精确包含搜索）

这些新字段与原有的 `query`、`exclude_query` 字段共存，但用途不同：
- `query`/`exclude_query`: 保留用于未来的模糊搜索、正则搜索（暂不开发）
- `keywords`/`exclude_keywords`: 用于精确的关键词包含搜索（当前开发）

## 实现细节

### 1. 前端类型定义更新 (`web/src/types/api.ts`)

在 `AdvancedSearchRequest` 接口中新增了两个字段：

```typescript
export interface AdvancedSearchRequest {
  query?: string | null              // 必须包含的关键词（模糊搜索、正则搜索，暂不开发）
  exclude_query?: string | null      // 不能包含的关键词（模糊搜索、正则搜索，暂不开发）
  keywords?: string[] | null         // 必须包含的关键词数组（精确包含搜索）
  exclude_keywords?: string[] | null // 不能包含的关键词数组（精确包含搜索）
  labels?: string | null             // 必须包含的标签（逗号分隔）
  exclude_labels?: string | null     // 不能包含的标签（逗号分隔）
  unlabeled_only?: boolean
  page?: number
  per_page?: number
}
```

### 2. 后端Schema更新 (`server/schemas.py`)

在 `SearchRequest` 类中新增了两个字段：

```python
class SearchRequest(BaseModel):
    """文本搜索请求的 schema。"""
    query: Optional[str] = Field(None, description="文本必须包含的关键词（模糊搜索、正则搜索，暂不开发）")
    exclude_query: Optional[str] = Field(None, description="文本不能包含的关键词（模糊搜索、正则搜索，暂不开发）")
    keywords: Optional[List[str]] = Field(None, description="文本必须包含的关键词数组（精确包含搜索）")
    exclude_keywords: Optional[List[str]] = Field(None, description="文本不能包含的关键词数组（精确包含搜索）")
    labels: Optional[str] = Field(None, description="文本必须包含的逗号分隔标签")
    exclude_labels: Optional[str] = Field(None, description="文本不能包含的逗号分隔标签")
    unlabeled_only: bool = Field(False, description="仅返回未标注文本")
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(50, description="每页记录数", ge=1, le=1000)
```

### 3. 后端服务层更新 (`server/services.py`)

在 `_build_search_query` 方法中添加了关键词数组的处理逻辑：

```python
# 应用关键词数组过滤器（精确包含搜索）
if search_request.keywords:
    for keyword in search_request.keywords:
        if keyword.strip():  # 跳过空关键词
            query = query.filter(AnnotationData.text.contains(keyword.strip()))

# 应用排除关键词数组过滤器（精确包含搜索）
if search_request.exclude_keywords:
    for keyword in search_request.exclude_keywords:
        if keyword.strip():  # 跳过空关键词
            query = query.filter(~AnnotationData.text.contains(keyword.strip()))
```

## 使用场景

### 1. 多关键词精确搜索
- 查找同时包含多个关键词的文本（AND逻辑）
- 例如：`keywords: ["weather", "today"]` 查找同时包含"weather"和"today"的文本

### 2. 批量排除关键词
- 排除包含任意一个指定关键词的文本
- 例如：`exclude_keywords: ["error", "invalid", "test"]` 排除包含错误、无效或测试数据

### 3. 精确的内容筛选
- 比原有的单一query字段更灵活
- 支持复杂的包含/排除逻辑组合

## API使用示例

### HTTP API调用示例

```bash
POST /annotations/search
Content-Type: application/json

{
    "keywords": ["weather", "today"],           # 必须同时包含这些关键词
    "exclude_keywords": ["bad", "error"],       # 不能包含这些关键词
    "labels": "intent, positive",               # 必须包含的标签
    "exclude_labels": "test, invalid",          # 不能包含的标签
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
    keywords=["weather", "forecast"],        # 必须包含这两个关键词
    exclude_keywords=["error", "invalid"],   # 不能包含这些关键词
    labels="intent",                         # 必须包含"intent"标签
    exclude_labels="test",                   # 不能包含"test"标签
    page=1,
    per_page=50
)

service = AnnotationService(db)
result = service.search_annotations(search_request)
```

### 前端TypeScript示例

```typescript
import { apiService } from '@/services/api'
import type { AdvancedSearchRequest } from '@/types/api'

const searchParams: AdvancedSearchRequest = {
  keywords: ['weather', 'forecast'],      // 必须包含的关键词数组
  exclude_keywords: ['error', 'invalid'], // 不能包含的关键词数组
  labels: 'intent, positive',             // 必须包含的标签
  exclude_labels: 'test',                 // 不能包含的标签
  page: 1,
  per_page: 20
}

const result = await apiService.advancedSearchAnnotations(searchParams)
```

## 逻辑说明

### 关键词搜索逻辑
- **keywords数组**: 使用AND逻辑，文本必须包含数组中的每一个关键词
- **exclude_keywords数组**: 使用OR逻辑，文本不能包含数组中的任意一个关键词
- **空值处理**: 自动过滤空字符串和空白字符串

### 与原有字段的关系
- `query` + `keywords`: 如果同时提供，文本必须满足所有条件
- `exclude_query` + `exclude_keywords`: 如果同时提供，文本不能满足任何一个排除条件
- 所有搜索条件（关键词、标签、未标注等）都是AND关系

## 性能考虑

1. **索引利用**: 新的关键词搜索仍然能够利用现有的文本索引
2. **查询优化**: 多个关键词通过链式filter应用，保持查询效率
3. **向后兼容**: 新字段为可选，不影响现有API调用

## 测试验证

创建了测试脚本验证功能：
- `tmp/test_keywords_search.py` - 直接服务层测试
- `tmp/demo_keywords_search_api.py` - HTTP API演示

## 批量更新支持

由于 `BulkUpdateLabelsRequest` 使用 `AdvancedSearchRequest` 作为搜索条件，新的关键词数组功能自动支持批量标签更新操作。

## 未来扩展

1. **模糊搜索**: 为 `query`/`exclude_query` 字段实现模糊匹配和正则表达式支持
2. **关键词权重**: 为不同关键词设置不同的匹配权重
3. **短语搜索**: 支持完整短语的精确匹配
4. **同义词扩展**: 支持同义词的自动扩展搜索

## 注意事项

1. 新字段为可选，保持向后兼容性
2. 关键词搜索使用精确包含匹配（case-sensitive）
3. 空关键词会被自动过滤
4. 所有搜索条件可以灵活组合使用 