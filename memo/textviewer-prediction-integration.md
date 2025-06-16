# TextViewer 预测功能集成

## 更新内容

### 简化数据展示
- **移除**: 文本统计信息（字符数、行数、单词数）
- **保留**: 基本文本信息（ID、字符数标签）和当前标签状态
- **优化**: 为预测功能留出更多空间

### 新增预测功能
- **意图预测**: 集成 `predictionService` 进行文本意图分析
- **实时反馈**: 显示预测状态（加载中、成功、失败）
- **详细结果**: 展示主要意图、置信度和所有意图得分
- **错误处理**: 完整的错误提示和处理机制

## 功能特性

### 1. 预测触发
```typescript
// 点击按钮或调用方法触发预测
const predictIntent = async () => {
  const response = await predictionService.predict(currentItem.text)
  // 显示结果
}
```

### 2. 结果展示
- **主要意图**: 最高得分的意图及其置信度
- **置信度可视化**: 
  - 绿色(success): ≥80%
  - 橙色(warning): 60%-79%
  - 红色(danger): <60%
- **详细得分**: 显示所有意图的得分排序

### 3. 状态管理
- `isLoading`: 预测加载状态
- `predictionResult`: 预测结果数据
- `predictionError`: 错误信息

## 使用方式

```vue
<template>
  <TextViewer :current-item="selectedItem" />
</template>

<script setup>
import TextViewer from '@/components/annotation/TextViewer.vue'
import type { AnnotationDataResponse } from '@/types/api'

const selectedItem = ref<AnnotationDataResponse | null>(null)
</script>
```

## UI 变化对比

### 之前
```
文本内容区域
├── 文本显示
├── 当前标签
└── 文本统计（字符数、行数、单词数）
```

### 现在
```
文本内容区域
├── 文本显示
├── 当前标签
└── 意图预测
    ├── 预测按钮
    ├── 主要结果（意图 + 置信度）
    ├── 详细得分列表
    └── 错误提示
```

## 技术细节

### 依赖项
- `predictionService`: 预测服务
- `ElMessage`: Element Plus 消息提示
- Vue 3 响应式状态管理

### 样式优化
- 统一的卡片样式
- 响应式布局
- 状态指示器
- 错误状态样式

## 配置要求

使用前需要在 AppHeader 中配置预测服务地址：
1. 点击用户头像 -> 设置
2. 配置预测服务 URL
3. 测试连接并保存

## 扩展建议

1. **批量预测**: 支持多个文本的批量意图预测
2. **历史记录**: 保存预测历史供后续查看
3. **自动预测**: 文本选中时自动触发预测
4. **结果对比**: 与人工标注结果进行对比分析
5. **导出功能**: 导出预测结果到文件 