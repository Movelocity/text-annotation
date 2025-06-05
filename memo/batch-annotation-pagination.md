# 批量标注页面分页功能实现

## 概述
为BatchAnnotationPage添加分页组件，解决筛选结果只能显示50条的限制问题。

## 修改内容

### 1. 修改 `useBatchAnnotation.ts` Composable

#### 新增分页相关计算属性
- `currentPage`: 当前页码
- `pageSize`: 每页数量  
- `totalPages`: 总页数

#### 修改筛选方法
- `filterTexts(resetPage = false)`: 支持重置页码参数
- 新筛选条件时重置到第一页
- 翻页时保持选择状态

#### 新增分页处理方法
- `handlePageChange(page: number)`: 处理页码变更
- `handlePageSizeChange(size: number)`: 处理每页数量变更

### 2. 修改 `BatchAnnotationPage.vue`

#### 添加分页组件
- 在ResultsList组件下方添加Pagination组件
- 传递分页相关props: currentPage, pageSize, total等
- 绑定分页事件处理器

#### 导入和使用
- 导入Pagination组件
- 从composable中获取分页相关状态和方法
- 修改筛选事件调用，确保新筛选时重置页码

#### 样式调整
- 添加`.pagination-section`样式
- 设置合适的padding和边框
- 保持与整体设计一致

### 3. 功能特性

#### 分页控制
- 支持上一页/下一页导航
- 支持直接跳转到指定页码
- 支持修改每页显示数量(20/50/100/200)

#### 状态管理
- 筛选条件变更时自动重置到第一页
- 翻页时保持当前筛选条件
- 加载状态时禁用分页操作

#### 用户体验
- 分页组件只在有结果时显示
- 与项目现有Pagination组件保持一致
- 响应式设计，适配不同屏幕尺寸

## 技术实现

### API集成
- 利用现有的`batchApi.filter()`方法
- 通过`page`和`perPage`参数控制分页
- 保持与后端API的兼容性

### 状态同步
- 分页状态存储在`state.filterOptions`中
- 与筛选条件统一管理
- 确保状态一致性

### 性能优化
- 只在必要时重新加载数据
- 保持选择状态在合理范围内
- 避免不必要的API调用

## 使用方式

1. 设置筛选条件后点击"筛选"
2. 查看筛选结果列表
3. 使用底部分页组件浏览更多结果
4. 可调整每页显示数量
5. 可直接跳转到指定页码

## 兼容性
- 完全向后兼容现有功能
- 不影响批量操作功能
- 保持现有的选择和更新逻辑
