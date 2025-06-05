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
      <ResultItem
        v-for="(text, index) in filteredTexts"
        :key="text.id"
        :item="text"
        :index="index + 1"
        :is-selected="isSelected(text.id)"
        @toggle-selection="$emit('toggleSelection', text.id)"
      />
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
import type { AnnotationDataResponse } from '@/types/api'
import ModernButton from '../common/ModernButton.vue'
import ResultItem from './ResultItem.vue'

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