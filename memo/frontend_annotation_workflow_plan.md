# 前端数据标注流程开发规划

## 📋 项目现状分析

**日期：** 2025年6月5日
**状态：** 阶段1开发完成 ✅
**负责：** AI Assistant + Developer协同

### 后端基础（✅ 已完善）
- **技术栈：** FastAPI + SQLAlchemy + SQLite
- **数据规模：** 114,304条标注数据，115个标签
- **API完整性：** 
  - 标注数据CRUD（创建、读取、更新、删除）
  - 标签管理（增删查）
  - 搜索和筛选（支持多条件）
  - 批量操作（批量标注）
  - 统计接口（系统统计、标签分布）
  - 健康检查

### 前端基础（✅ 已扩展完成）
- **技术栈：** Vue 3 + TypeScript + Element Plus + Pinia
- **已有架构：**
  - ✅ stores：annotation.ts, label.ts, app.ts
  - ✅ services：api.ts（完整的API封装）
  - ✅ types：api.ts（完整的类型定义）
  - ✅ router：基础路由配置
- **当前页面：** 
  - ✅ HomePage.vue（统计展示 + 导航入口）
  - ✅ AnnotationPage.vue（核心标注工作台）
- **核心组件：** 
  - ✅ TextList.vue（文本列表组件）
  - ✅ TextViewer.vue（文本查看器）
  - ✅ LabelSelector.vue（标签选择器）

## 🎯 Minimal数据标注流程设计

### 核心用户场景
1. **标注员快速标注**：查看文本 → 分配标签 → 跳转下一条 ✅
2. **批量处理**：选择多条文本 → 批量分配标签 ⏸️
3. **数据管理**：筛选、搜索、统计标注进度 ✅
4. **标签管理**：添加、删除、修改标签 ⏸️

### 工作流程设计
```
[选择筛选条件] → [文本列表展示] → [选择文本] → [查看内容] → [分配标签] → [自动跳转下一条] ✅
                                    ↓
[批量选择] → [批量标注] → [返回列表] ⏸️
```

## 📁 前端架构规划

### 页面结构
```
web/src/pages/
├── HomePage.vue          # ✅ 统计展示页面（已有）
├── AnnotationPage.vue    # ✅ 核心标注工作台（已完成）
└── LabelManagePage.vue   # ⏸️ 标签管理页面（待开发）
```

### 组件设计
```
web/src/components/
├── annotation/           # ✅ 标注相关组件（已完成）
│   ├── TextList.vue      # ✅ 文本列表（分页、筛选、搜索）
│   ├── TextViewer.vue    # ✅ 文本内容展示
│   ├── LabelSelector.vue # ✅ 标签选择器（支持快捷键）
│   └── BatchOperations.vue # ⏸️ 批量操作工具（待开发）
├── label/               # ⏸️ 标签管理组件（待开发）
│   ├── LabelForm.vue    # ⏸️ 标签表单
│   └── LabelStats.vue   # ⏸️ 标签统计
└── common/              # ⏸️ 通用组件（待开发）
    ├── PageHeader.vue   # ⏸️ 页面头部
    └── LoadingState.vue # ⏸️ 加载状态
```

### 路由规划
```javascript
const routes = [
  { path: '/', redirect: '/home' },
  { path: '/pages/home', component: HomePage },           // ✅ 统计首页
  { path: '/pages/annotation', component: AnnotationPage }, // ✅ 标注工作台
  { path: '/pages/labels', component: LabelManagePage },   // ⏸️ 标签管理
  { path: '/pages/annotation/:id', component: AnnotationDetail } // ⏸️ 单条详情（可选）
]
```

## 🚀 分阶段实施计划

### 阶段1：核心标注功能（✅ 已完成，2024年6月5日）

**目标：** 实现基础的标注工作流程

**已完成任务：**
1. **✅ AnnotationPage.vue** - 主标注工作台
   - 三栏布局：文本列表 | 当前文本 | 标签选择器
   - 基础的文本展示和标签分配
   - 简单的筛选（已标注/未标注）
   - 智能导航（自动跳转到下一个未标注项）

2. **✅ TextList组件**
   - 分页文本列表（支持20/50/100/200条每页）
   - 点击选择当前文本
   - 标注状态指示器（已标注/未标注）
   - 实时搜索和筛选功能
   - 防抖搜索优化

3. **✅ LabelSelector组件**
   - 标签选择界面（网格布局）
   - 保存标注功能
   - 跳转下一条功能
   - **快捷键支持：** 数字键1-9选择标签、Enter保存、Space跳过
   - 标签搜索功能

4. **✅ TextViewer组件**
   - 文本内容完整显示
   - 文本统计信息（字符数、行数、单词数）
   - 当前标签状态显示

5. **✅ 路由集成**
   - 添加 `/annotation` 路由
   - 在首页添加"开始标注"入口

**实际验收结果：**
- ✅ 能够浏览文本列表
- ✅ 能够为文本分配标签
- ✅ 能够保存标注并跳转下一条
- ✅ 基础的筛选功能正常
- ✅ 快捷键操作流畅
- ✅ 三栏布局响应式适配

### 阶段2：标签管理（⏸️ 规划中，优先级：中）

**目标：** 完善标签管理功能

**任务清单：**
1. **LabelManagePage.vue** - 标签管理页面
2. **LabelForm组件** - 添加/编辑标签
3. **LabelStats组件** - 标签使用统计

**验收标准：**
- [ ] 能够查看所有标签
- [ ] 能够添加新标签
- [ ] 能够删除标签
- [ ] 显示标签使用统计

### 阶段3：增强功能（⏸️ 规划中，优先级：低）

**目标：** 提升用户体验和操作效率

**任务清单：**
1. **快捷键支持** ✅ 
   - ✅ 1-9数字键对应前9个标签
   - ✅ Enter保存，Space跳过
   - ⏸️ 方向键导航文本

2. **批量操作**
   - ⏸️ 多选文本功能
   - ⏸️ 批量分配标签
   - ⏸️ 批量删除

3. **高级筛选** ✅（部分完成）
   - ✅ 按标签筛选
   - ✅ 文本内容搜索
   - ⏸️ 日期范围筛选

4. **进度跟踪**
   - ✅ 标注进度条（页面顶部统计）
   - ⏸️ 工作会话统计
   - ⏸️ 自动保存标注位置

## 💡 设计原则（✅ 已实现）

### 1. 效率优先 ✅
- **✅ 快捷键支持**：数字键、Enter、Space键
- **✅ 自动跳转**：标注完成自动到下一条未标注
- **✅ 智能筛选**：防抖搜索、状态筛选

### 2. 用户体验 ✅
- **✅ 清晰布局**：三栏式，信息层次分明
- **✅ 实时反馈**：操作结果即时显示
- **✅ 响应式设计**：适配不同屏幕尺寸

### 3. 技术稳健 ✅
- **✅ 复用现有架构**：充分利用stores和API
- **✅ 类型安全**：TypeScript全覆盖
- **✅ 组件复用**：Element Plus组件一致性

## 🔧 技术实施细节（✅ 已实现）

### 数据流设计 ✅
```javascript
// 标注工作台的数据流
AnnotationPage.vue
├── 使用 annotationStore.searchAnnotations() 获取文本列表
├── 使用 labelStore.fetchLabels() 获取标签列表
├── 使用 annotationStore.updateAnnotation() 保存标注
└── 响应式更新UI状态
```

### 状态管理扩展 ✅
```javascript
// annotationStore 现有状态（充分利用）
{
  annotations: [],          // 当前文本列表
  currentAnnotation: null,  // 当前选中文本
  searchParams: {},         // 搜索参数
  total: 0,                // 总数量
  loading: false           // 加载状态
}
```
