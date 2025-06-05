# 前端开发指南

## 项目概述

文本标注系统前端需要提供用户友好的界面，用于文本标注、标签管理、数据导入和统计查看等功能。

## 后端服务信息

- **服务地址**: `http://localhost:8000`
- **API文档**: 见 `docs/api.md`
- **快速参考**: 见 `docs/api-quick-reference.md`

## 推荐技术栈

### 基础框架
- **React** (推荐) + TypeScript
- **Vue.js** + TypeScript
- **Angular** + TypeScript

### UI组件库
- **Ant Design** (React)
- **Element Plus** (Vue)
- **Angular Material** (Angular)

### 状态管理
- **Redux Toolkit** (React)
- **Pinia** (Vue)
- **NgRx** (Angular)

### HTTP客户端
- **Axios** 或 **Fetch API**

## 核心功能模块

### 1. 文本列表与标注页面

**主要功能**:
- 分页展示文本列表
- 搜索和过滤功能
- 单个文本标注
- 批量选择和批量标注

**API调用**:
```javascript
// 获取文本列表
const getTexts = async (params) => {
  const response = await fetch('/annotations/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: params.search,
      labels: params.filterLabels,
      unlabeled_only: params.showUnlabeledOnly,
      page: params.page,
      per_page: params.pageSize
    })
  });
  return response.json();
};

// 更新标注
const updateAnnotation = async (id, labels) => {
  const response = await fetch(`/annotations/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ labels })
  });
  return response.json();
};

// 批量标注
const bulkLabel = async (textIds, labels) => {
  const response = await fetch('/annotations/bulk-label', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text_ids: textIds,
      labels: labels
    })
  });
  return response.json();
};
```

**UI建议**:
- 使用表格组件展示文本列表
- 每行显示：ID、文本预览、当前标签、操作按钮
- 支持多选用于批量操作
- 标签输入框支持自动完成
- 搜索框实现防抖

### 2. 标签管理页面

**主要功能**:
- 查看所有标签
- 创建新标签
- 删除标签
- 显示每个标签的使用统计

**API调用**:
```javascript
// 获取所有标签
const getLabels = async () => {
  const response = await fetch('/labels/');
  return response.json();
};

// 创建标签
const createLabel = async (labelName) => {
  const response = await fetch('/labels/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label: labelName })
  });
  return response.json();
};

// 删除标签
const deleteLabel = async (labelId) => {
  await fetch(`/labels/${labelId}`, {
    method: 'DELETE'
  });
};
```

### 3. 数据导入页面

**主要功能**:
- 文件上传和导入
- 批量文本输入
- 导入进度显示
- 导入结果反馈

**实现建议**:
```javascript
// 文件导入
const importFile = async (filePath) => {
  const response = await fetch('/import/text-file', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_path: filePath })
  });
  return response.json();
};

// 批量导入文本
const importTexts = async (texts) => {
  const response = await fetch('/annotations/import-texts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texts })
  });
  return response.json();
};
```

**注意事项**:
- 文件路径需要是服务器可访问的绝对路径
- 可以考虑实现文件浏览器组件
- 大文件导入时显示进度条

### 4. 统计仪表板

**主要功能**:
- 显示系统整体统计
- 标签使用情况图表
- 标注进度追踪

**API调用**:
```javascript
// 获取系统统计
const getStats = async () => {
  const response = await fetch('/stats');
  return response.json();
};
```

**图表推荐**:
- 使用 **Chart.js** 或 **ECharts**
- 饼图显示标注/未标注比例
- 柱状图显示各标签使用频率

## 状态管理建议

### React + Redux Toolkit 示例

```javascript
// store/slices/annotationSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchAnnotations = createAsyncThunk(
  'annotations/fetchAnnotations',
  async (params) => {
    const response = await fetch('/annotations/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return response.json();
  }
);

const annotationSlice = createSlice({
  name: 'annotations',
  initialState: {
    items: [],
    total: 0,
    page: 1,
    loading: false,
    error: null
  },
  reducers: {
    setPage: (state, action) => {
      state.page = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnnotations.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAnnotations.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items;
        state.total = action.payload.total;
      })
      .addCase(fetchAnnotations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  }
});
```

### Vue + Pinia 示例

```javascript
// stores/annotation.js
import { defineStore } from 'pinia';

export const useAnnotationStore = defineStore('annotation', {
  state: () => ({
    annotations: [],
    total: 0,
    page: 1,
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchAnnotations(params) {
      this.loading = true;
      try {
        const response = await fetch('/annotations/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(params)
        });
        const data = await response.json();
        this.annotations = data.items;
        this.total = data.total;
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    }
  }
});
```

## 性能优化建议

### 1. 分页和虚拟滚动
- 使用分页避免一次性加载大量数据
- 对于长列表考虑虚拟滚动

### 2. 搜索防抖
```javascript
import { debounce } from 'lodash';

const debouncedSearch = debounce((query) => {
  // 执行搜索
  searchAnnotations(query);
}, 300);
```

### 3. 缓存标签列表
```javascript
// 标签列表不经常变化，可以缓存
const labelsCache = {
  data: null,
  timestamp: null,
  ttl: 5 * 60 * 1000, // 5分钟

  async getLabels() {
    const now = Date.now();
    if (!this.data || !this.timestamp || (now - this.timestamp) > this.ttl) {
      const response = await fetch('/labels/');
      this.data = await response.json();
      this.timestamp = now;
    }
    return this.data;
  }
};
```

### 4. 错误处理
```javascript
const apiCall = async (url, options) => {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error('API调用失败:', error);
    // 显示用户友好的错误信息
    throw error;
  }
};
```

## 用户体验建议

### 1. 加载状态
- 为所有异步操作显示加载指示器
- 长时间操作显示进度条

### 2. 操作反馈
- 成功操作显示提示信息
- 失败操作显示错误详情
- 关键操作需要确认对话框

### 3. 键盘快捷键
- `Ctrl+S`: 保存当前标注
- `Tab`: 切换到下一个文本
- `Shift+Tab`: 切换到上一个文本

### 4. 响应式设计
- 支持移动设备访问
- 适配不同屏幕尺寸

## 开发环境设置

### 1. 启动后端服务
```bash
cd C:\projects\data\intents-dataset
uv run app.main:app
```

### 2. 代理设置（开发环境）
```javascript
// vite.config.js (Vite)
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}

// package.json (Create React App)
{
  "proxy": "http://localhost:8000"
}
```

## 部署建议

### 1. 构建优化
- 启用代码分割
- 压缩静态资源
- 使用CDN加速

### 2. 生产环境配置
- 配置正确的API基础URL
- 启用HTTPS
- 设置适当的CORS策略

这份指南应该能帮助你快速开始前端开发工作。如果在开发过程中遇到问题，可以随时参考详细的API文档。 