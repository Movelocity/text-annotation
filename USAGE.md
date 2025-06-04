# 文本标注系统 - 快速使用指南

## 🚀 快捷命令（推荐）

我们已在 `pyproject.toml` 中注册了快捷命令，使用起来更简单：

### 启动服务器
```bash
uv run server
```
服务器将在 http://localhost:8000 启动，带有自动重载功能。

### 数据导入
```bash
uv run import-data
```
自动导入 `archive/old-data/` 目录下的所有标注数据。

### API演示
```bash
uv run demo
```
运行API功能演示（需要先启动服务器）。

## 📖 查看API文档

启动服务器后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 开发命令

### 代码格式化
```bash
uv run ruff format .
```

### 代码检查
```bash
uv run ruff check .
```

## 📊 系统状态

启动服务器后访问健康检查端点：
```bash
curl http://localhost:8000/health
```

## 🆘 备用命令

如果快捷命令有问题，可以使用传统方式：

```bash
# 启动服务器
uv run python -m app.main

# 数据导入
uv run python -m scripts.run_import

# API演示
uv run python -m scripts.demo
```

## 📁 数据目录结构

确保数据目录结构正确：
```
archive/
└── old-data/
    ├── label_config.yaml
    └── <label_directories>/
        └── *.txt
```

## 💡 小贴士

1. **首次使用**：先运行 `uv run import-data` 导入数据
2. **开发环境**：运行 `uv run server` 启动服务器
3. **API测试**：使用 `uv run demo` 测试所有功能
4. **查看统计**：导入完成后会自动显示数据统计信息 