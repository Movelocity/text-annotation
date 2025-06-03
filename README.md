# 文本标注后端系统

基于 FastAPI 的文本标注和标记后端系统，使用 SQLite 数据库管理标注数据，提供完整的 REST API 接口。

## 功能特性

- **标注数据管理**: 存储和管理带有关联标签的文本（无重复）
- **标签管理**: 管理带有 ID 和标签字符串的标签定义
- **数据导入**: 导入现有的已标注数据和新的未标注文本
- **搜索与过滤**: 支持文本查询和标签过滤的高级搜索
- **统计分析**: 全面的统计数据和分析
- **批量操作**: 批量标注和文本导入
- **RESTful API**: 基于 FastAPI 的完整 REST API，支持自动文档生成

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架，用于构建 API
- **SQLAlchemy**: SQL 工具包和 ORM
- **SQLite**: 轻量级数据库
- **Pydantic**: 使用 Python 类型注解进行数据验证
- **UV**: 快速的 Python 包安装器和解析器

## 项目结构

```
text-annotation/
├── main.py           # FastAPI 应用程序，包含所有端点
├── models.py         # SQLAlchemy 数据库模型
├── schemas.py        # 用于 API 验证的 Pydantic schemas
├── services.py       # 业务逻辑层
├── data_import.py    # 核心数据导入工具库，提供数据导入、标签同步等功能
├── run_import.py     # 数据库初始化和统计信息显示脚本
├── README.md         # 本文件
└── pyproject.toml    # 项目配置和依赖项
```

## 安装与设置

### 前置要求

- Python 3.12+
- UV 包管理器

### 设置步骤

1. **克隆并设置项目**（已完成）:
   ```bash
   cd text-annotation
   ```

2. **安装依赖项**（已完成）:
   ```bash
   uv sync
   ```

3. **导入现有数据**:
   ```bash
   uv run python run_import.py
   ```

4. **启动服务器**:
   ```bash
   uv run python main.py
   ```

   API 将在 `http://localhost:8000` 可用

5. **访问 API 文档**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 数据库 Schema

### AnnotationData 表
- `id`: 主键（自动生成）
- `text`: 文本内容（唯一，无重复）
- `labels`: 逗号分隔的标签字符串

### Labels 表
- `id`: 标签的唯一标识符
- `label`: 标签字符串（唯一）

## API 端点

### 健康检查
- `GET /health` - 健康检查端点

### 标注数据管理
- `POST /annotations/` - 创建新标注
- `GET /annotations/{id}` - 根据 ID 获取标注
- `PUT /annotations/{id}` - 更新标注
- `DELETE /annotations/{id}` - 删除标注
- `POST /annotations/search` - 搜索和过滤标注
- `POST /annotations/bulk-label` - 批量标注多个文本
- `POST /annotations/import-texts` - 导入多个文本

### 标签管理
- `POST /labels/` - 创建新标签
- `GET /labels/` - 获取所有标签
- `GET /labels/{id}` - 根据 ID 获取标签
- `DELETE /labels/{id}` - 删除标签

### 数据导入
- `POST /import/old-data` - 导入旧的标注数据
- `POST /import/label-config` - 导入标签配置
- `POST /import/text-file` - 导入文本文件

### 统计信息
- `GET /stats/system` - 获取系统统计信息

## 使用示例

### 1. 搜索标注

```bash
curl -X POST "http://localhost:8000/annotations/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "product",
       "page": 1,
       "per_page": 10
     }'
```

### 2. 创建新标注

```bash
curl -X POST "http://localhost:8000/annotations/" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "这是一个示例文本",
       "labels": "product,question"
     }'
```

### 3. 仅获取未标注文本

```bash
curl -X POST "http://localhost:8000/annotations/search" \
     -H "Content-Type: application/json" \
     -d '{
       "unlabeled_only": true,
       "page": 1,
       "per_page": 50
     }'
```

### 4. 批量标注多个文本

```bash
curl -X POST "http://localhost:8000/annotations/bulk-label" \
     -H "Content-Type: application/json" \
     -d '{
       "text_ids": [1, 2, 3],
       "labels": "product,inquiry"
     }'
```

### 5. 获取系统统计信息

```bash
curl -X GET "http://localhost:8000/stats/system"
```

### 6. 导入新文本

```bash
curl -X POST "http://localhost:8000/annotations/import-texts" \
     -H "Content-Type: application/json" \
     -d '{
       "texts": [
         "待标注的新文本",
         "另一个用于标注的文本"
       ]
     }'
```

## 数据导入流程

系统处理两种类型的数据导入：

### 1. 旧标注数据
- 位于 `archive/old-data/**/*.txt` 结构中
- 每个文件表示一个标签，每行是该标签的文本记录
- 跨文件的重复文本将被合并，标签用逗号分隔
- 示例: `old-data/product/askStock.txt` → 文本被标记为 "askStock"

### 2. 新未标注数据
- 按行分隔的文本文件
- 每行成为一个没有标签的新标注记录
- 可通过 API 或文件上传进行导入

## 开发

### 开发模式运行

```bash
# 启动带自动重载的服务器
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 数据库操作

SQLite 数据库会自动创建为 `annotation.db`。你可以使用任何 SQLite 客户端检查它：

```bash
sqlite3 annotation.db
.tables
.schema annotation_data
.schema labels
```

### 添加新功能

1. **模型**: 在 `models.py` 中添加新表
2. **Schemas**: 在 `schemas.py` 中添加验证 schema
3. **服务**: 在 `services.py` 中添加业务逻辑
4. **端点**: 在 `main.py` 中添加 API 端点

## 配置

### 环境变量
- `DATABASE_URL`: SQLite 数据库 URL（默认: `sqlite:///./annotation.db`）

### CORS 设置
当前配置为开发环境（`allow_origins=["*"]`）。在生产环境中，请配置特定的来源。

## 生产部署

生产部署时：

1. **更新 CORS 设置**：在 `main.py` 中
2. **配置合适的数据库**：建议生产环境使用 PostgreSQL
3. **添加身份验证**和授权
4. **设置适当的日志记录**
5. **使用生产 ASGI 服务器**：如使用 Uvicorn workers 的 Gunicorn

```bash
# 生产环境命令示例
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 许可证

本项目是用于管理标注数据集的文本标注系统的一部分。
