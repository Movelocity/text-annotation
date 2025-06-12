# 批量标注功能使用指南

## 概述

批量标注功能允许标注员通过设置筛选条件来批量选择文本，然后为这些文本批量添加或删除标签。这大大提高了标注工作的效率。

## 功能特性

- ✅ **高级筛选**: 支持包含/排除关键词、包含/排除标签等多种筛选条件
- ✅ **预览功能**: 可以预览筛选结果，确认无误后再执行批量操作
- ✅ **批量更新**: 支持批量添加标签、删除标签或同时进行两种操作
- ✅ **两种模式**: 支持通过筛选条件批量操作，也支持选中特定文本ID批量操作
- ✅ **响应式状态管理**: 提供 Vue Composable 进行状态管理
- ✅ **类型安全**: 完整的 TypeScript 类型定义

## 核心文件结构

```
frontend/src/
├── types/api.ts                     # API 类型定义
├── services/
│   ├── api.ts                      # 基础 API 服务
│   ├── batchAnnotation.ts          # 批量标注服务
│   └── README.md                   # 本文档
├── composables/
│   └── useBatchAnnotation.ts       # 批量标注 Composable
└── utils/
    └── batchAnnotationExamples.ts  # 使用示例
```

## 快速开始

### 1. 基础 API 使用

```typescript
import { annotationApi, batchApi } from '@/services/api'

// 高级搜索
const result = await annotationApi.advancedSearch({
  query: '客服',              // 包含关键词
  exclude_query: '测试',      // 排除关键词
  labels: '客户服务',         // 包含标签
  exclude_labels: '已处理',   // 排除标签
  page: 1,
  per_page: 50
})

// 批量更新标签
const updateResult = await annotationApi.bulkUpdateLabels({
  search_criteria: {
    query: '客服',
    labels: '待处理'
  },
  labels_to_add: '已审核,质量确认',
  labels_to_remove: '待处理'
})
```

### 2. 使用批量标注服务

```typescript
import { batchApi } from '@/services/batchAnnotation'

// 筛选文本
const filteredTexts = await batchApi.filter({
  includeKeywords: ['客服', '咨询'],
  excludeKeywords: ['测试'],
  includeLabels: ['客户服务'],
  excludeLabels: ['已处理']
})

// 为筛选结果添加标签
const result = await batchApi.addLabels(
  { includeKeywords: ['客服'] },
  ['已审核', '质量确认']
)

// 预览筛选结果
const preview = await batchApi.preview({
  includeKeywords: ['投诉']
})
```

### 3. 使用 Vue Composable

```vue
<script setup lang="ts">
import { useBatchAnnotation } from '@/composables/useBatchAnnotation'

const {
  state,
  hasFilterConditions,
  selectedTextsCount,
  filterTexts,
  previewFilter,
  addLabelsToFiltered,
  addLabelsToSelected,
  selectAll,
  clearSelection
} = useBatchAnnotation()

// 设置筛选条件
state.filterOptions.includeKeywords = ['客服']
state.filterOptions.excludeLabels = ['已处理']

// 执行筛选
await filterTexts()

// 批量添加标签
await addLabelsToFiltered(['已审核'])
</script>
```

## API 参考

### 筛选条件 (BatchFilterOptions)

```typescript
interface BatchFilterOptions {
  includeKeywords?: string[]    // 必须包含的关键词
  excludeKeywords?: string[]    // 不能包含的关键词
  includeLabels?: string[]      // 必须包含的标签
  excludeLabels?: string[]      // 不能包含的标签
  unlabeledOnly?: boolean       // 只显示未标注的文本
  page?: number                 // 页码
  perPage?: number             // 每页数量
}
```

### 更新选项 (BatchUpdateOptions)

```typescript
interface BatchUpdateOptions {
  addLabels?: string[]     // 要添加的标签
  removeLabels?: string[]  // 要删除的标签
}
```

### 主要方法

#### batchApi 方法

```typescript
// 筛选相关
batchApi.filter(options: BatchFilterOptions)           // 筛选文本
batchApi.preview(options: BatchFilterOptions)          // 预览筛选结果

// 批量更新
batchApi.updateByFilter(filterOptions, updateOptions)  // 通过筛选条件更新
batchApi.updateByIds(textIds, updateOptions)          // 通过ID列表更新

// 便利方法
batchApi.addLabels(filterOptions, labels)             // 添加标签
batchApi.removeLabels(filterOptions, labels)          // 删除标签
batchApi.addLabelsToTexts(textIds, labels)           // 为指定文本添加标签
batchApi.removeLabelsFromTexts(textIds, labels)      // 从指定文本删除标签
```

## 使用场景示例

### 场景 1: 客服文本分类

```typescript
// 1. 筛选包含客服关键词但未分类的文本
const customerServiceTexts = await batchApi.filter({
  includeKeywords: ['客服', '咨询', '问题'],
  excludeLabels: ['已分类']
})

// 2. 批量添加"客户服务"标签
await batchApi.addLabels(
  { includeKeywords: ['客服', '咨询'], excludeLabels: ['已分类'] },
  ['客户服务', '待处理']
)
```

### 场景 2: 质量审核

```typescript
// 1. 筛选已初步标注但未审核的文本
const unreviewed = await batchApi.filter({
  includeLabels: ['客户服务'],
  excludeLabels: ['已审核']
})

// 2. 预览将要审核的文本
const preview = await batchApi.preview({
  includeLabels: ['客户服务'],
  excludeLabels: ['已审核']
})

// 3. 批量添加审核标签
await batchApi.addLabels(
  { includeLabels: ['客户服务'], excludeLabels: ['已审核'] },
  ['已审核']
)
```

### 场景 3: 紧急处理

```typescript
// 1. 筛选包含紧急关键词的文本
const urgentTexts = await batchApi.filter({
  includeKeywords: ['紧急', '急', '马上', '立即']
})

// 2. 同时添加"紧急"标签和删除"待处理"标签
await batchApi.updateByFilter(
  { includeKeywords: ['紧急', '急'] },
  { 
    addLabels: ['紧急', '高优先级'],
    removeLabels: ['待处理', '普通']
  }
)
```

### 场景 4: 数据清理

```typescript
// 删除测试数据的标签
await batchApi.removeLabels(
  { includeKeywords: ['测试', 'test'] },
  ['客户服务', '生产数据']
)

// 为测试数据添加标识
await batchApi.addLabels(
  { includeKeywords: ['测试', 'test'] },
  ['测试数据', '待删除']
)
```

## 最佳实践

### 1. 使用预览功能

在执行批量操作前，建议先使用预览功能确认影响范围：

```typescript
// 先预览
const preview = await batchApi.preview(filterOptions)
console.log(`将影响 ${preview.totalCount} 条记录`)

// 确认无误后执行
if (preview.totalCount < 1000) {  // 安全检查
  await batchApi.addLabels(filterOptions, ['新标签'])
}
```

### 2. 分页处理大量数据

```typescript
const filterOptions = {
  includeKeywords: ['客服'],
  page: 1,
  perPage: 100  // 控制每次处理的数量
}

let page = 1
let hasMore = true

while (hasMore) {
  const result = await batchApi.filter({ ...filterOptions, page })
  
  // 处理当前页的数据
  await batchApi.updateByIds(
    result.items.map(item => item.id),
    { addLabels: ['已处理'] }
  )
  
  page++
  hasMore = result.items.length === filterOptions.perPage
}
```

### 3. 错误处理

```typescript
try {
  const result = await batchApi.addLabels(filterOptions, ['新标签'])
  console.log(`成功更新 ${result.updated_count} 条记录`)
} catch (error) {
  console.error('批量操作失败:', error)
  // 处理错误，如显示用户友好的错误信息
}
```

### 4. 状态管理

使用 Composable 进行状态管理：

```vue
<script setup lang="ts">
const batch = useBatchAnnotation()

// 响应式筛选条件
watchEffect(() => {
  console.log('当前筛选条件:', batch.state.filterOptions)
  console.log('是否有筛选条件:', batch.hasFilterConditions.value)
})

// 自动刷新
watch(() => batch.state.filterOptions, () => {
  if (batch.hasFilterConditions.value) {
    batch.previewFilter()
  }
}, { deep: true })
</script>
```

## 注意事项

1. **性能考虑**: 批量操作可能影响性能，建议控制每次处理的数据量
2. **权限控制**: 确保用户有相应的标注权限
3. **数据备份**: 批量操作前建议备份重要数据
4. **日志记录**: 记录批量操作的日志，便于追踪和回滚
5. **用户体验**: 提供进度指示和操作确认，避免误操作

## 版本更新

- **v1.0.0**: 初始版本，支持基本的批量筛选和更新功能
- 后续版本将根据使用反馈持续优化和扩展功能 