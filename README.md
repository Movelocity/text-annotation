# 文本标注系统

基于 FastAPI 的文本标注和标记后端系统，用于个人PC上进行数据标注和数据管理。

## 快速开始

### 安装依赖
```bash
uv sync
```

### 快捷命令

#### 启动服务器
```bash
# 方式1：使用快捷命令（推荐）
uv run server

# 方式2：使用完整命令名
uv run text-annotation-server

# 方式3：传统方式
uv run python -m server.main
```

#### 数据导入
```bash
# 方式1：使用快捷命令（推荐）
uv run import-data

# 方式2：使用完整命令名  
uv run text-annotation-import

# 方式3：传统方式
uv run python -m scripts.run_import
```

#### API演示
```bash
# 方式1：使用快捷命令（推荐）
uv run demo

# 方式2：使用完整命令名
uv run text-annotation-demo

# 方式3：传统方式
uv run python -m scripts.demo
```

## API 文档

启动服务器后，访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看交互式 API 文档。

## 项目结构

```
text-annotation/
├── server/              # 核心应用代码
│   ├── main.py       # FastAPI应用主文件
│   ├── models.py     # 数据库模型
│   ├── schemas.py    # Pydantic模型
│   ├── services.py   # 业务逻辑服务
│   └── config.py     # 配置管理
├── scripts/          # 工具脚本
│   ├── run_import.py # 数据导入脚本
│   ├── data_import.py # 数据导入工具
│   └── demo.py       # API演示脚本
├── tests/            # 测试目录
├── logs/             # 日志目录
├── memo/             # 开发文档
└── pyproject.toml    # 项目配置
```

## 开发

### 开发环境设置
```bash
# 安装开发依赖
uv sync --group dev

# 代码格式化
uv run ruff format .

# 代码检查
uv run ruff check .
```

### 数据库

项目使用 SQLite 数据库，数据库文件为 `annotation.db`。

## 功能特性

- ✅ 标注数据的 CRUD 操作
- ✅ 标签管理
- ✅ 数据搜索和过滤
- ✅ 批量标注操作
- ✅ 数据导入导出
- ✅ 统计和分析
- ✅ 健康检查端点

## 许可证

MIT License
