# API 快速参考

## 基础URL
```
http://localhost:8000
```

## 标注数据 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/annotations/` | 创建标注 |
| GET | `/annotations/{id}` | 获取标注 |
| PUT | `/annotations/{id}` | 更新标注 |
| DELETE | `/annotations/{id}` | 删除标注 |
| POST | `/annotations/search` | 搜索标注（支持高级筛选） |
| POST | `/annotations/bulk-label` | 批量标注（覆盖） |
| POST | `/annotations/bulk-update-labels` | 批量标签更新（增删） |
| POST | `/annotations/import-texts` | 导入文本 |

## 标签管理 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/labels/` | 创建标签 |
| GET | `/labels/` | 获取所有标签 |
| GET | `/labels/{id}` | 获取标签 |
| PUT | `/labels/{id}` | 更新标签 |
| DELETE | `/labels/{id}` | 删除标签 |

## 数据导入 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/import/text-file` | 导入文本文件 |
| POST | `/import/old-data` | 导入旧数据 |
| POST | `/import/label-config` | 导入标签配置 |

## 统计 API

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/stats` | 系统统计 |
| GET | `/health` | 健康检查 |

## 常用请求示例

### 高级搜索文本（增强版）
```javascript
POST /annotations/search
{
  "query": "客服",                    // 必须包含
  "exclude_query": "测试",            // 不能包含
  "labels": "客户服务,咨询",           // 必须包含标签
  "exclude_labels": "已处理",         // 不能包含标签
  "unlabeled_only": false,
  "page": 1,
  "per_page": 50
}
```

### 创建标注
```javascript
POST /annotations/
{
  "text": "要标注的文本",
  "labels": "标签1,标签2"
}
```

### 批量标注（覆盖现有标签）
```javascript
POST /annotations/bulk-label
{
  "text_ids": [1, 2, 3],
  "labels": "新标签1,新标签2"
}
```

### 批量标签更新（增删标签）
```javascript
// 方式1：通过搜索条件筛选
POST /annotations/bulk-update-labels
{
  "search_criteria": {
    "query": "客服",
    "labels": "待处理",
    "page": 1,
    "per_page": 1000
  },
  "labels_to_add": "已审核,质量确认",
  "labels_to_remove": "待处理"
}

// 方式2：通过ID列表
POST /annotations/bulk-update-labels
{
  "text_ids": [1, 2, 3, 4, 5],
  "labels_to_add": "已审核",
  "labels_to_remove": "待处理"
}
```

### 创建标签
```javascript
POST /labels/
{
  "label": "新标签名称",
  "description": "标签描述",        // 可选
  "groups": "分类1/子分类1/标签组"   // 可选
}
```

### 更新标签
```javascript
PUT /labels/{id}
{
  "label": "更新后的标签名称",
  "description": "更新后的描述",     // 可选
  "groups": "更新后的分组"          // 可选
}
```

## 响应格式

### 分页响应
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 50
}
```

### 批量更新响应
```json
{
  "updated_count": 15,
  "message": "批量更新完成。操作: 添加标签: 已审核; 删除标签: 待处理。更新了 15 条记录。"
}
```

### 系统统计
```json
{
  "total_texts": 1000,
  "labeled_texts": 600,
  "unlabeled_texts": 400,
  "total_labels": 10,
  "label_statistics": [...]
}
``` 