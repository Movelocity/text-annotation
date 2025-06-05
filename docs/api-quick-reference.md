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
| POST | `/annotations/search` | 搜索标注（分页） |
| POST | `/annotations/bulk-label` | 批量标注 |
| POST | `/annotations/import-texts` | 导入文本 |

## 标签管理 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/labels/` | 创建标签 |
| GET | `/labels/` | 获取所有标签 |
| GET | `/labels/{id}` | 获取标签 |
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

### 搜索文本（分页）
```javascript
POST /annotations/search
{
  "query": "搜索内容",
  "page": 1,
  "per_page": 50,
  "unlabeled_only": false
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

### 批量标注
```javascript
POST /annotations/bulk-label
{
  "text_ids": [1, 2, 3],
  "labels": "新标签1,新标签2"
}
```

### 创建标签
```javascript
POST /labels/
{
  "label": "新标签名称"
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