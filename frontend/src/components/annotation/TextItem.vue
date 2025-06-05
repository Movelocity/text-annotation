<!--
  文本项组件（简化版）
  功能：显示单个文本项，支持选择状态
-->
<template>
  <div
    class="text-item"
    :class="{ 
      'selected': isSelected,
      'labeled': item.labels
    }"
    @click="handleClick"
  >
    <!-- 头部：ID + 状态 -->
    <div class="item-header">
      <span class="item-id">#{{ item.id }}</span>
      <div class="label-container">
        <template v-if="itemLabels.length > 0">
          <el-tag
            v-for="label in itemLabels.slice(0, 2)"
            :key="label"
            type="success"
            size="small"
            class="item-label"
          >
            {{ label }}
          </el-tag>
          <span v-if="itemLabels.length > 2" class="more-labels">
            +{{ itemLabels.length - 2 }}
          </span>
        </template>
        <span v-else class="item-status pending">待标注</span>
      </div>
    </div>
    
    <!-- 内容区 -->
    <div class="item-content">
      <p class="text-preview">{{ truncateText(item.text, 120) }}</p>
    </div>
    
    <!-- 底部：元数据 -->
    <div class="item-footer">
      <span class="meta-info">{{ item.text.length }} 字符</span>
      <span class="meta-info">{{ item.text.split('\n').length }} 行</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AnnotationDataResponse } from '../../types/api'

// Props
interface Props {
  item: AnnotationDataResponse
  index: number
  isSelected?: boolean
}

// Emits
interface Emits {
  (e: 'click', item: AnnotationDataResponse, index: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 计算属性
const itemLabels = computed(() => {
  if (!props.item.labels) return []
  return props.item.labels.split(',').map(label => label.trim()).filter(label => label)
})

// 方法
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const handleClick = () => {
  emit('click', props.item, props.index)
}
</script>

<style scoped>
/* 简化的文本项样式 */
.text-item {
  padding: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.text-item:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.text-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

/* 头部样式 */
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.item-id {
  font-weight: 600;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  flex-shrink: 0;
}

.label-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  max-width: 60%;
}

.item-label {
  font-size: 11px;
}

.more-labels {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  background: var(--el-bg-color-page);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--el-border-color-light);
}

.item-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.item-status.success {
  background: var(--el-color-success-light-9);
  color: var(--el-color-success);
}

.item-status.pending {
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning);
}

/* 内容样式 */
.item-content {
  margin-bottom: 12px;
}

.text-preview {
  margin: 0;
  color: var(--el-text-color-primary);
  line-height: 1.5;
  font-size: 14px;
  word-break: break-word;
}

/* 底部样式 */
.item-footer {
  display: flex;
  gap: 16px;
}

.meta-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style> 