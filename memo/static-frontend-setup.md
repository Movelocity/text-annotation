# 静态前端集成配置

## 配置概述

已将 FastAPI 后端配置为直接提供前端静态文件服务，无需单独启动前端开发服务器。

## 配置详情

### 1. 静态文件挂载

在 `app/main.py` 中添加了以下配置：

```python
# 挂载静态资源目录
app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
# 挂载其他静态文件（如 vite.svg）
app.mount("/static", StaticFiles(directory=static_dir), name="static")
```

### 2. 前端页面路由

- **根路径** (`/`): 提供 `index.html` 文件
- **SPA 路由** (`/pages/*`): 将所有页面路径转发给前端路由器处理
- **资源路径** (`/assets/*`): 提供 CSS、JS 等构建资源
- **图标路径** (`/vite.svg`): 提供 Vite 图标文件

### 3. 文件路径结构

```
frontend/
└── dist/           # 前端构建输出目录
    ├── index.html  # 主页面文件
    ├── vite.svg    # Vite 图标
    └── assets/     # 静态资源目录
        ├── *.js    # JavaScript 文件
        ├── *.css   # CSS 文件
        └── *.map   # Source map 文件
```

## 使用方法

### 1. 构建前端项目

```bash
cd frontend
pnpm build
```

### 2. 启动后端服务

```bash
uv run python start_server.py
# 或者
uv run python -m app.main
```

### 3. 访问应用

打开浏览器访问: `http://localhost:8000`

- 前端页面将直接由 FastAPI 提供
- API 端点仍然可以通过 `/annotations/*`, `/labels/*` 等路径访问
- 静态资源自动加载，无需额外配置

## 优势

1. **简化部署**: 只需启动一个服务
2. **统一端口**: 前后端使用相同端口，避免 CORS 问题
3. **生产就绪**: 适合生产环境部署
4. **开发友好**: 前端修改后重新构建即可生效

## SPA 路由支持

### 前端路由处理

添加了 `/pages/{path:path}` 路由来支持 SPA 的客户端路由：

```python
@app.get("/pages/{path:path}")
async def serve_spa_pages(path: str):
    # 返回 index.html，让前端路由器处理页面导航
    return FileResponse(index_file)
```

### 路由示例

以下路径都会返回 `index.html`，由前端路由器处理：
- `/pages/annotation` → 标注页面
- `/pages/labels` → 标签管理页面
- `/pages/batch` → 批量标注页面
- `/pages/statistics` → 统计页面

## 注意事项

1. 前端修改后需要重新构建（`pnpm build`）才能生效
2. 开发期间如需热重载，仍可使用 `pnpm dev` 独立启动前端
3. 确保 `frontend/dist` 目录存在且包含构建文件
4. API 路由优先级高于静态文件路由
5. 所有 `/pages/*` 路径都会由前端路由器处理，确保前端路由配置正确

## 验证方法

1. 启动后端服务
2. 访问 `http://localhost:8000` 确认前端页面正常加载
3. 检查开发者工具网络面板，确认静态资源正常加载
4. 测试 API 功能，确认前后端交互正常 