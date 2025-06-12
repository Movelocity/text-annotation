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

## 新增功能使用指南

### 1. 高级搜索功能
新的搜索API支持更精确的筛选条件：

```javascript
// 高级搜索示例
const searchWithAdvancedFilters = async () => {
  const searchParams = {
    query: "客服",                    // 必须包含"客服"
    exclude_query: "测试",            // 不能包含"测试"
    labels: "客户服务,咨询",           // 必须包含这些标签之一
    exclude_labels: "已处理,已关闭",   // 不能包含这些标签
    unlabeled_only: false,
    page: 1,
    per_page: 50
  };

  const response = await fetch('/annotations/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(searchParams)
  });

  return response.json();
};
```

#### 前端界面建议：
- 提供"包含关键词"和"排除关键词"两个输入框
- 提供"必须包含标签"和"排除标签"的多选组件
- 添加"仅显示未标注"的复选框

### 2. 批量标签更新功能
新的批量更新API支持增加或删除标签，而不是完全覆盖：

```javascript
// 基于搜索条件的批量更新
const bulkUpdateBySearch = async () => {
  const updateRequest = {
    search_criteria: {
      query: "客服问题",
      labels: "待处理",
      page: 1,
      per_page: 1000  // 确保获取所有匹配的记录
    },
    labels_to_add: "已审核,质量确认",     // 添加新标签
    labels_to_remove: "待处理"           // 删除指定标签
  };

  const response = await fetch('/annotations/bulk-update-labels', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updateRequest)
  });

  return response.json();
};

// 基于ID列表的批量更新
const bulkUpdateByIds = async (selectedIds) => {
  const updateRequest = {
    text_ids: selectedIds,
    labels_to_add: "已审核",
    labels_to_remove: "待处理"
  };

  const response = await fetch('/annotations/bulk-update-labels', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updateRequest)
  });

  return response.json();
};
```

#### 推荐的工作流程：
1. **标注员筛选模式**：
   - 使用高级搜索找到需要处理的文本
   - 对搜索结果进行人工审核
   - 确认后批量添加标签

2. **质量控制模式**：
   - 筛选已标注但未审核的文本
   - 审核后批量添加"已审核"标签
   - 对有问题的文本批量添加"需修改"标签

#### 前端界面建议：

```jsx
// React 组件示例
function BatchLabelUpdate() {
  const [searchCriteria, setSearchCriteria] = useState({});
  const [selectedIds, setSelectedIds] = useState([]);
  const [labelsToAdd, setLabelsToAdd] = useState('');
  const [labelsToRemove, setLabelsToRemove] = useState('');

  const handleBatchUpdate = async () => {
    const request = {
      ...(selectedIds.length > 0 
        ? { text_ids: selectedIds } 
        : { search_criteria: searchCriteria }
      ),
      labels_to_add: labelsToAdd || undefined,
      labels_to_remove: labelsToRemove || undefined
    };

    try {
      const result = await bulkUpdateLabels(request);
      alert(`成功更新 ${result.updated_count} 条记录`);
    } catch (error) {
      alert(`更新失败: ${error.message}`);
    }
  };

  return (
    <div>
      {/* 搜索条件或ID选择 */}
      {/* 标签添加/删除输入框 */}
      <button onClick={handleBatchUpdate}>批量更新</button>
    </div>
  );
}
```

### 3. 工作流程优化建议

#### 标注员工作流：
1. **初步筛选**：使用高级搜索找到相似文本
2. **批量预览**：显示搜索结果供确认
3. **批量标注**：对确认的文本批量添加标签
4. **逐个微调**：对需要特殊处理的文本单独标注

#### 质量控制流程：
1. **筛选待审核**：查找已标注但未审核的文本
2. **审核标注**：人工检查标注质量
3. **批量确认**：对合格的文本批量添加"已审核"标签
4. **问题标记**：对有问题的文本添加"需修改"标签

## 用户体验建议

### 1. 加载状态
- 为所有异步操作显示加载指示器
- 长时间操作显示进度条
- 批量操作时显示操作进度和预估完成时间

### 2. 操作反馈
- 成功操作显示提示信息
- 失败操作显示错误详情
- 关键操作需要确认对话框
- 批量操作前显示将要影响的记录数量

### 3. 键盘快捷键
- `Ctrl+S`: 保存当前标注
- `Tab`: 切换到下一个文本
- `Shift+Tab`: 切换到上一个文本
- `Ctrl+A`: 全选当前页的文本（用于批量操作）

### 4. 响应式设计
- 支持移动设备访问
- 适配不同屏幕尺寸
- 移动端优化批量操作界面

## 开发环境设置

### 1. 启动后端服务
```bash
cd C:\projects\data\intents-dataset
uv run server.main:app
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