# ResultsList 关键词高亮功能使用说明

## 功能概述

`ResultsList` 组件现在支持接收一组字符串关键词，在搜索结果中自动高亮显示这些关键词。

## 新增属性

### keywords (可选)
- **类型**: `string[]`
- **默认值**: `[]`
- **描述**: 需要在搜索结果中高亮显示的关键词数组

## 使用示例

```vue
<template>
  <ResultsList
    :filtered-texts="searchResults"
    :total-count="totalCount"
    :selected-texts-count="selectedCount"
    :is-loading="loading"
    :has-filter-conditions="hasConditions"
    :is-selected="isItemSelected"
    :keywords="highlightKeywords"
    @select-all="handleSelectAll"
    @clear-selection="handleClearSelection"
    @toggle-selection="handleToggleSelection"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ResultsList from '@/components/batch/ResultsList.vue'

// 关键词数组 - 这些词会在结果中被高亮
const highlightKeywords = ref([
  '数据标注',
  '机器学习',
  'AI',
  '自然语言处理'
])

// 其他状态...
</script>
```

## 高亮效果

- 关键词将以黄色背景高亮显示
- 高亮是大小写不敏感的
- 支持多个关键词同时高亮
- 特殊字符会被自动转义，确保安全性

## 样式特性

- 渐变黄色背景 (#fff3cd 到 #ffeaa7)
- 深黄色文字 (#856404)
- 圆角边框
- 轻微阴影效果
- 加粗字体

## 技术实现

1. **安全性**: 使用正则表达式转义特殊字符，防止 XSS 攻击
2. **性能**: 通过计算属性优化渲染性能
3. **兼容性**: 向后兼容，keywords 属性为可选参数