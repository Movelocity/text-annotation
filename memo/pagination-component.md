# 分页组件替换记录

## 更改概述
将 TextList.vue 中的 Element Plus 分页组件替换为项目内的简洁分页组件。

## 最新优化（紧凑版）
针对窄宽度容器（500px以内）进行了专门优化，采用垂直布局减少横向空间占用。

## 新增文件
- `frontend/src/components/common/Pagination.vue` - 新的简洁分页组件

## 修改文件
- `frontend/src/components/annotation/TextList.vue` - 替换分页组件引用和相关样式

## 功能特性

### 新分页组件功能
1. **页面导航**：上一页、下一页按钮
2. **页码跳转**：输入框直接跳转到指定页码
3. **每页数量设置**：下拉选择每页显示条数
4. **状态显示**：显示总条数和当前页码/总页数
5. **禁用状态**：支持加载时禁用所有操作
6. **响应式设计**：移动端友好的布局调整

### 接口设计
```typescript
// Props
interface Props {
  currentPage: number      // 当前页码
  pageSize: number        // 每页数量
  total: number           // 总条数
  pageSizes?: number[]    // 可选的每页数量选项，默认 [20, 50, 100, 200]
  disabled?: boolean      // 是否禁用，默认 false
}

// 事件
interface Emits {
  (e: 'page-change', page: number): void      // 页码变化
  (e: 'size-change', size: number): void      // 每页数量变化
}
```

## 样式特点
1. **紧凑设计**：专为窄宽度容器优化，垂直布局节省横向空间
2. **极简元素**：按钮只保留图标，文字简化，减少占用
3. **两行布局**：顶行显示统计，底行显示导航控制
4. **小尺寸元素**：所有组件都采用较小的尺寸适配窄容器
5. **一致性**：与项目整体设计风格保持一致
6. **交互反馈**：hover、focus 状态清晰的视觉反馈
7. **CSS 变量**：使用项目统一的 CSS 变量系统

## 优势
1. **减少依赖**：不依赖 Element Plus 分页组件
2. **定制性强**：完全控制样式和行为
3. **体积更小**：相比 Element Plus 的完整分页组件更轻量
4. **维护性好**：代码清晰，易于修改和扩展
5. **空间高效**：专为窄容器优化，纵向占用最小化
6. **移动友好**：在400px以下有特殊优化处理

## 使用示例
```vue
<Pagination
  :current-page="currentPage"
  :page-size="pageSize"
  :page-sizes="[20, 50, 100, 200]"
  :total="total"
  :disabled="loading"
  @page-change="handlePageChange"
  @size-change="handleSizeChange"
/>
```

## 兼容性
- 完全向后兼容原有的 TextList 组件接口
- 保持相同的事件处理逻辑
- 样式风格与项目整体设计保持一致 