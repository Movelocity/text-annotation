<!--
  搜索结果项组件
-->
<template>
  <div
    class="result-item"
    :class="{ selected: isSelected }"
    @click="$emit('toggleSelection')"
  >
    <!-- 序号角标 -->
    <div class="item-index">{{ index }}</div>
    
    <div class="item-header">
      <el-checkbox
        :model-value="isSelected"
        @change="$emit('toggleSelection')"
        @click.stop
      />
      <span class="item-id">ID: {{ item.id }}</span>
      <div class="item-labels">
        <el-tag
          v-for="label in getLabelsArray(item.labels)"
          :key="label"
          size="small"
          type="info"
        >
          {{ label }}
        </el-tag>
        <span v-if="getLabelsArray(item.labels).length === 0" class="no-labels">
          未标注
        </span>
      </div>
    </div>
    <div 
      class="item-content"
      :class="{ expandable: item.text.length > 200, expanded: expandedItems.has(item.id) }"
      @click.stop="toggleExpanded(item.id)"
    >
      <div class="text-content">
        {{ getDisplayText(item) }}
      </div>
      <div 
        v-if="item.text.length > 200" 
        class="expand-indicator"
        :title="expandedItems.has(item.id) ? '点击收起' : '点击展开全文'"
      >
        <i :class="expandedItems.has(item.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { AnnotationDataResponse } from '@/types/api'
import { parseLabels } from '@/utils/labelUtils'

// Props
interface Props {
  item: AnnotationDataResponse
  index: number
  isSelected: boolean
}

// Emits
interface Emits {
  'toggleSelection': []
}

defineProps<Props>()
defineEmits<Emits>()

// 展开状态管理
const expandedItems = ref<Set<number>>(new Set())

// 方法
const getLabelsArray = (labels: string | null | undefined): string[] => {
  return parseLabels(labels)
}

const toggleExpanded = (id: number) => {
  if (expandedItems.value.has(id)) {
    expandedItems.value.delete(id)
  } else {
    expandedItems.value.add(id)
  }
}

const getDisplayText = (text: AnnotationDataResponse): string => {
  if (text.text.length <= 100 || expandedItems.value.has(text.id)) {
    return text.text
  }
  return text.text.substring(0, 100) + '...'
}
</script>

<style scoped>
.result-item {
  position: relative;
  padding: var(--spacing-md);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-sm);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.result-item:hover {
  border-color: var(--el-color-primary-light-7);
  background: var(--el-color-primary-light-9);
}

.result-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  box-shadow: var(--shadow-sm);
}

/* 序号角标 */
.item-index {
  position: absolute;
  top: 0px;
  right: 0px;
  background: var(--el-color-info-light-8);
  color: gray;
  width: 36px;
  height: 24px;
  border-radius: 0 var(--radius-md);;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  z-index: 1;
}

.item-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.item-id {
  font-size: 12px;
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.item-labels {
  display: flex;
  gap: var(--spacing-xs);
  flex: 1;
  flex-wrap: wrap;
}

.no-labels {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.item-content {
  padding-left: 26px;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  line-height: 1.5;
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
}

.item-content.expandable {
  cursor: pointer;
  transition: background-color var(--duration-fast) ease;
  padding: var(--spacing-xs) var(--spacing-sm);
  margin-left: 14px;
  border-radius: var(--radius-sm);
}

.item-content.expandable:hover {
  background-color: var(--el-color-primary-light-9);
  border-radius: var(--radius-sm);
}

.text-content {
  flex: 1;
  word-break: break-word;
}

.expand-indicator {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--el-color-primary);
  opacity: 0.7;
  transition: opacity var(--duration-fast) ease;
}

.item-content.expandable:hover .expand-indicator {
  opacity: 1;
}

.expand-indicator i {
  font-size: 12px;
}

.item-content.expanded .text-content {
  white-space: pre-wrap;
}
</style>
