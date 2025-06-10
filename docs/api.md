# 文本标注系统 API 文档

## 基本信息

- **基础URL**: `http://localhost:8000`
- **API版本**: 1.0.0
- **标题**: 文本标注 API
- **描述**: 文本标注和标记系统的后端 API

## 认证

当前版本不需要认证，适用于本地开发环境。

## 数据模型

### AnnotationData（标注数据）

```json
{
  "id": 1,
  "text": "这是一段需要标注的文本",
  "labels": "意图识别,情感分析"
}
```

### Label（标签）

```json
{
  "id": 1,
  "label": "意图识别",
  "description": "标签的详细描述",
  "groups": "分类1/子分类1/标签组"
}
```

### SystemStats（系统统计）

```json
{
  "total_texts": 1000,
  "labeled_texts": 600,
  "unlabeled_texts": 400,
  "total_labels": 10,
  "label_statistics": [
    {
      "label": "意图识别",
      "count": 150
    }
  ]
}
```

## API 端点

### 1. 标注数据管理

#### 1.1 创建标注数据

- **POST** `/annotations/`
- **描述**: 创建新的标注数据
- **请求体**:
```json
{
  "text": "要标注的文本内容",
  "labels": "标签1,标签2"  // 可选，逗号分隔
}
```
- **响应**: 201 Created
```json
{
  "id": 1,
  "text": "要标注的文本内容",
  "labels": "标签1,标签2"
}
```
- **错误**: 400 Bad Request - 文本已存在

#### 1.2 获取单个标注数据

- **GET** `/annotations/{annotation_id}`
- **描述**: 根据ID获取标注数据
- **路径参数**:
  - `annotation_id` (integer): 标注的ID
- **响应**: 200 OK
```json
{
  "id": 1,
  "text": "文本内容",
  "labels": "标签1,标签2"
}
```
- **错误**: 404 Not Found - 标注未找到

#### 1.3 更新标注数据

- **PUT** `/annotations/{annotation_id}`
- **描述**: 更新标注数据
- **路径参数**:
  - `annotation_id` (integer): 要更新的标注ID
- **请求体**:
```json
{
  "labels": "新标签1,新标签2"  // 可选
}
```
- **响应**: 200 OK
```json
{
  "id": 1,
  "text": "文本内容",
  "labels": "新标签1,新标签2"
}
```
- **错误**: 404 Not Found - 标注未找到

#### 1.4 删除标注数据

- **DELETE** `/annotations/{annotation_id}`
- **描述**: 删除标注数据
- **路径参数**:
  - `annotation_id` (integer): 要删除的标注ID
- **响应**: 204 No Content
- **错误**: 404 Not Found - 标注未找到

#### 1.5 搜索标注数据（增强版）

- **POST** `/annotations/search`
- **描述**: 搜索和过滤标注数据，支持分页和高级筛选条件
- **请求体**:
```json
{
  "query": "搜索文本内容",           // 可选，文本必须包含的关键词
  "exclude_query": "排除关键词",     // 可选，文本不能包含的关键词
  "labels": "标签1,标签2",          // 可选，文本必须包含的标签（逗号分隔）
  "exclude_labels": "标签3,标签4",   // 可选，文本不能包含的标签（逗号分隔）
  "unlabeled_only": false,         // 是否只返回未标注文本
  "page": 1,                       // 页码，从1开始
  "per_page": 50                   // 每页数量，最大1000
}
```
- **响应**: 200 OK
```json
{
  "items": [
    {
      "id": 1,
      "text": "文本内容",
      "labels": "标签1,标签2"
    }
  ],
  "total": 100,      // 总记录数
  "page": 1,         // 当前页码
  "per_page": 50     // 每页记录数
}
```

#### 1.6 批量标注

- **POST** `/annotations/bulk-label`
- **描述**: 为多个文本批量应用标签（覆盖现有标签）
- **请求体**:
```json
{
  "text_ids": [1, 2, 3],        // 要标注的文本ID列表
  "labels": "标签1,标签2"        // 要应用的标签
}
```
- **响应**: 200 OK
```json
{
  "updated_count": 3
}
```

#### 1.7 批量标签更新（新增功能）

- **POST** `/annotations/bulk-update-labels`
- **描述**: 批量添加或删除标签，支持搜索条件筛选或指定ID列表
- **特性**:
  - 支持通过搜索条件筛选目标数据后批量操作
  - 支持直接指定文本ID列表批量操作
  - 支持添加标签（保留现有标签）
  - 支持删除指定标签（保留其他标签）
  - 支持同时添加和删除不同标签

- **请求体方式1**（通过搜索条件）:
```json
{
  "search_criteria": {
    "query": "客服",                    // 包含"客服"关键词
    "exclude_query": "测试",            // 不包含"测试"关键词
    "labels": "客户服务",               // 包含"客户服务"标签
    "exclude_labels": "已处理",         // 不包含"已处理"标签
    "unlabeled_only": false,
    "page": 1,
    "per_page": 1000
  },
  "labels_to_add": "审核完成,质量确认",    // 要添加的标签
  "labels_to_remove": "待处理"           // 要删除的标签
}
```

- **请求体方式2**（通过ID列表）:
```json
{
  "text_ids": [1, 2, 3, 4, 5],         // 要更新的文本ID列表
  "labels_to_add": "审核完成,质量确认",    // 要添加的标签
  "labels_to_remove": "待处理"           // 要删除的标签
}
```

- **响应**: 200 OK
```json
{
  "updated_count": 15,
  "message": "批量更新完成。操作: 添加标签: 审核完成, 质量确认; 删除标签: 待处理。更新了 15 条记录。"
}
```

- **使用场景**:
  - **标注员筛选**: 使用搜索条件找到特定类型的文本，然后批量添加标签
  - **质量审核**: 筛选已完成初步标注的文本，批量添加"已审核"标签
  - **标签清理**: 删除过时或错误的标签
  - **状态更新**: 为完成某个流程的文本批量更新状态标签

#### 1.8 批量导入文本

- **POST** `/annotations/import-texts`
- **描述**: 导入多个文本作为未标注数据
- **请求体**:
```json
{
  "texts": [
    "第一段文本",
    "第二段文本",
    "第三段文本"
  ]
}
```
- **响应**: 200 OK
```json
{
  "imported_count": 3
}
```

### 2. 标签管理

#### 2.1 创建标签

- **POST** `/labels/`
- **描述**: 创建新标签
- **请求体**:
```json
{
  "label": "新标签名称",
  "description": "标签的详细描述",    // 可选
  "groups": "分类1/子分类1/标签组",   // 可选，标签分组
  "id": 10                         // 可选，自定义ID
}
```
- **响应**: 201 Created
```json
{
  "id": 1,
  "label": "新标签名称",
  "description": "标签的详细描述",
  "groups": "分类1/子分类1/标签组"
}
```
- **错误**: 400 Bad Request - 标签已存在

#### 2.2 获取所有标签

- **GET** `/labels/`
- **描述**: 获取所有标签列表
- **响应**: 200 OK
```json
[
  {
    "id": 1,
    "label": "意图识别",
    "description": "识别用户意图类型",
    "groups": "NLP/意图/分类"
  },
  {
    "id": 2,
    "label": "情感分析",
    "description": "分析文本情感倾向",
    "groups": "NLP/情感/分析"
  }
]
```

#### 2.3 获取单个标签

- **GET** `/labels/{label_id}`
- **描述**: 根据ID获取标签
- **路径参数**:
  - `label_id` (integer): 标签ID
- **响应**: 200 OK
```json
{
  "id": 1,
  "label": "意图识别",
  "description": "识别用户意图类型",
  "groups": "NLP/意图/分类"
}
```
- **错误**: 404 Not Found - 标签未找到

#### 2.4 更新标签

- **PUT** `/labels/{label_id}`
- **描述**: 更新标签信息
- **路径参数**:
  - `label_id` (integer): 要更新的标签ID
- **请求体**:
```json
{
  "label": "更新后的标签名称",
  "description": "更新后的标签描述",    // 可选
  "groups": "更新后的标签分组"        // 可选
}
```
- **响应**: 200 OK
```json
{
  "id": 1,
  "label": "更新后的标签名称",
  "description": "更新后的标签描述",
  "groups": "更新后的标签分组"
}
```
- **错误**: 
  - 404 Not Found - 标签未找到
  - 400 Bad Request - 标签名称与其他标签重复

#### 2.5 删除标签

- **DELETE** `/labels/{label_id}`
- **描述**: 删除标签
- **路径参数**:
  - `label_id` (integer): 要删除的标签ID
- **响应**: 204 No Content
- **错误**: 404 Not Found - 标签未找到

### 3. 数据导入

#### 3.1 导入文本文件

- **POST** `/import/text-file`
- **描述**: 从文本文件批量导入数据（高性能版本）
- **请求体**:
```json
{
  "file_path": "C:/path/to/textfile.txt"
}
```
- **响应**: 200 OK
```json
{
  "imported_count": 1000,
  "file_path": "C:/path/to/textfile.txt",
  "file_size": 1048576,
  "status": "success"
}
```
- **错误**:
  - 404 Not Found - 文件未找到
  - 403 Forbidden - 文件无读取权限
  - 413 Payload Too Large - 文件过大（>100MB）
  - 400 Bad Request - 文件编码错误

#### 3.2 导入旧数据

- **POST** `/import/old-data`
- **描述**: 导入旧的标注数据
- **查询参数**:
  - `old_data_path` (string): 旧数据路径，默认为 "../old-data"
- **响应**: 200 OK
```json
{
  "files_processed": 5,
  "records_imported": 1000,
  "duplicates_merged": 50
}
```
- **错误**:
  - 404 Not Found - 路径未找到
  - 500 Internal Server Error - 导入失败

#### 3.3 导入标签配置

- **POST** `/import/label-config`
- **描述**: 从YAML配置文件导入标签
- **查询参数**:
  - `config_path` (string): 配置文件路径，默认为 "../old-data/label_config.yaml"
- **响应**: 200 OK
```json
{
  "imported_labels": 10
}
```
- **错误**:
  - 404 Not Found - 配置文件未找到
  - 500 Internal Server Error - 导入失败

### 4. 统计信息

#### 4.1 获取系统统计

- **GET** `/stats` 或 `/stats/system`
- **描述**: 获取系统整体统计信息
- **响应**: 200 OK
```json
{
  "total_texts": 1000,
  "labeled_texts": 600,
  "unlabeled_texts": 400,
  "total_labels": 10,
  "label_statistics": [
    {
      "label": "意图识别",
      "count": 150
    },
    {
      "label": "情感分析",
      "count": 120
    }
  ]
}
```

### 5. 健康检查

#### 5.1 健康检查

- **GET** `/health`
- **描述**: 检查API服务状态
- **响应**: 200 OK
```json
{
  "status": "healthy",
  "message": "文本标注 API 正在运行"
}
```

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足 |
| 404 | 资源未找到 |
| 413 | 请求体过大 |
| 500 | 服务器内部错误 |

## 前端开发建议

### 主要功能模块

1. **文本列表页面**: 展示所有文本，支持搜索、过滤、分页
2. **标注页面**: 对单个文本进行标注，显示可用标签
3. **批量标注页面**: 选择多个文本进行批量标注
4. **标签管理页面**: 创建、删除、查看标签
5. **数据导入页面**: 上传文件导入数据
6. **统计仪表板**: 显示系统统计信息

### 推荐的状态管理

- 使用分页加载避免一次性加载大量数据
- 实现搜索防抖，避免频繁请求
- 缓存标签列表，减少重复请求
- 批量操作时显示进度条

### 示例前端调用

```javascript
// 获取标注数据
const response = await fetch('/annotations/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    page: 1,
    per_page: 50,
    unlabeled_only: false
  })
});
const data = await response.json();

// 创建标注
await fetch('/annotations/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: '这是要标注的文本',
    labels: '标签1,标签2'
  })
});
``` 