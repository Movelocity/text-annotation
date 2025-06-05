<!--
  筛选结果列表组件
-->
<template>
  <div class="results-list-panel glass-panel">
    <div class="section-header">
      <h2>
        <i class="fas fa-list"></i>
        筛选结果
        <span v-if="totalCount > 0" class="count-badge">{{ totalCount }}</span>
      </h2>
      <div class="result-actions" v-if="filteredTexts.length > 0">
        <ModernButton
          text="全选"
          icon="fas fa-check-square"
          @click="$emit('selectAll')"
          :disabled="selectedTextsCount === filteredTexts.length"
        />
        <ModernButton
          text="清空选择"
          icon="fas fa-times"
          @click="$emit('clearSelection')"
          :disabled="selectedTextsCount === 0"
        />
      </div>
    </div>

    <!-- 结果列表 -->
    <div class="results-list" v-if="filteredTexts.length > 0">
      <div
        v-for="text in filteredTexts"
        :key="text.id"
        class="result-item"
        :class="{ selected: isSelected(text.id) }"
        @click="$emit('toggleSelection', text.id)"
      >
        <div class="item-header">
          <el-checkbox
            :model-value="isSelected(text.id)"
            @change="$emit('toggleSelection', text.id)"
            @click.stop
          />
          <span class="item-id">ID: {{ text.id }}</span>
          <div class="item-labels">
            <el-tag
              v-for="label in getLabelsArray(text.labels)"
              :key="label"
              size="small"
              type="info"
            >
              {{ label }}
            </el-tag>
            <span v-if="getLabelsArray(text.labels).length === 0" class="no-labels">
              未标注
            </span>
          </div>
        </div>
        <div 
          class="item-content"
          :class="{ expandable: text.text.length > 200, expanded: expandedItems.has(text.id) }"
          @click.stop="toggleExpanded(text.id)"
        >
          <div class="text-content">
            {{ getDisplayText(text) }}
          </div>
          <div 
            v-if="text.text.length > 200" 
            class="expand-indicator"
            :title="expandedItems.has(text.id) ? '点击收起' : '点击展开全文'"
          >
            <i :class="expandedItems.has(text.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!isLoading" class="empty-state">
      <i class="fas fa-search"></i>
      <p>{{ hasFilterConditions ? '没有找到匹配的文本' : '请设置筛选条件后执行筛选' }}</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>正在筛选数据...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { AnnotationDataResponse } from '@/types/api'
import { parseLabels } from '@/utils/labelUtils'
import ModernButton from '../common/ModernButton.vue'

// Props
interface Props {
  filteredTexts: AnnotationDataResponse[]
  totalCount: number
  selectedTextsCount: number
  isLoading: boolean
  hasFilterConditions: boolean
  isSelected: (id: number) => boolean
}

defineProps<Props>()

// Emits
interface Emits {
  'selectAll': []
  'clearSelection': []
  'toggleSelection': [id: number]
}

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
.results-list-panel {
  padding: var(--spacing-xl);
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  flex-shrink: 0;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.count-badge {
  background: var(--el-color-primary);
  color: white;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  margin-left: var(--spacing-sm);
}

.result-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.results-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  margin-top: var(--spacing-md);
  padding-right: 8px;
  min-height: 0;
}

.result-item {
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

/* 空状态和加载状态 */
.empty-state, .loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-4xl);
  color: var(--el-text-color-placeholder);
  text-align: center;
}

.empty-state i, .loading-state i {
  font-size: 48px;
  margin-bottom: var(--spacing-lg);
  opacity: 0.5;
}

.loading-state i {
  color: var(--el-color-primary);
  opacity: 0.8;
}

/* 自定义滚动条样式 */
.results-list::-webkit-scrollbar {
  width: 6px;
}

.results-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.results-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
  transition: background var(--duration-fast) ease;
}

.results-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style> 