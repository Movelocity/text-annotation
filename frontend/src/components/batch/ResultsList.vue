<!--
  筛选结果列表组件 - 优化版
  采用精简白色卡片效果展示搜索结果
-->
<template>
  <div class="results-list-panel">
    <!-- 结果统计和操作栏 -->
    <div class="results-header">
      <div class=" results-title">
        <i class="fas fa-list-ul"></i>
        筛选结果
        
        <div class="results-stats" v-if="totalCount > 0">
          <span class="total-count">共 {{ totalCount }} 条</span>
          <el-tag v-if="selectedTextsCount > 0" type="primary" size="default">
            已选择 {{ selectedTextsCount }} 条
          </el-tag>
        </div>
      </div>
      
      <div class="results-actions" v-if="filteredTexts.length > 0">
        <el-button
          type="primary"
          size="default"
          @click="$emit('selectAll')"
          :disabled="selectedTextsCount === filteredTexts.length"
          :title="selectedTextsCount === filteredTexts.length ? '已全选' : '全选当前结果'"
        >
          <i class="fas fa-check-double"></i>
          全选
        </el-button>
        <el-button
          type="primary"
          size="default"
          @click="$emit('clearSelection')"
          :disabled="selectedTextsCount === 0"
          :title="selectedTextsCount === 0 ? '暂无选择项' : '清空选择'"
        >
          <i class="fas fa-times-circle"></i>
          清空
        </el-button>
      </div>
    </div>

    <!-- 结果列表容器 -->
    <div class="results-container" v-if="filteredTexts.length > 0">
      <div class="results-list">
        <ResultItem
          v-for="(text, index) in filteredTexts"
          :key="text.id"
          :item="text"
          :index="index + 1"
          :is-selected="isSelected(text.id)"
          @toggle-selection="$emit('toggleSelection', text.id)"
        />
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!isLoading" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-search"></i>
      </div>
      <div class="empty-title">
        {{ hasFilterConditions ? '未找到匹配结果' : '请设置筛选条件' }}
      </div>
      <div class="empty-description">
        {{ hasFilterConditions ? '请尝试调整筛选条件重新搜索' : '在左侧面板设置筛选条件后点击筛选按钮' }}
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else class="loading-state">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <div class="loading-text">正在搜索...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AnnotationDataResponse } from '@/types/api'
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
  background: var(--background-light);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--card-shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 结果头部 */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px 16px 24px;
  background: linear-gradient(135deg, #f8fafb 0%, #ffffff 100%);
  border-bottom: 1px solid var(--divider-color);
  flex-shrink: 0;
}

.results-info {
  flex: 1;
}

.results-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.results-title i {
  color: var(--primary-color);
  font-size: 16px;
}

.results-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
}

.total-count {
  color: var(--text-secondary);
  font-weight: 500;
}

.selected-count {
  color: var(--primary-color);
  font-weight: 600;
  background: var(--primary-color);
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(25, 118, 210, 0.15) 100%);
  padding: 2px 8px;
  border-radius: 12px;
  border: 1px solid rgba(25, 118, 210, 0.2);
}

/* 操作按钮 */
.results-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--background-light);
  color: var(--text-secondary);
  border: 1px solid var(--divider-color);
}

.action-btn:hover:not(:disabled) {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.action-btn i {
  font-size: 12px;
}

/* 结果容器 */
.results-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.results-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px 20px 20px;
  display: flex;
  flex-direction: column;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f1f3f4 0%, #e8eaed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.empty-icon i {
  font-size: 32px;
  color: var(--text-secondary);
  opacity: 0.6;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 300px;
}

/* 加载状态 */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  text-align: center;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(25, 118, 210, 0.2) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.loading-spinner i {
  font-size: 24px;
  color: var(--primary-color);
}

.loading-text {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 滚动条样式 */
.results-list::-webkit-scrollbar {
  width: 6px;
}

.results-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 3px;
}

.results-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
  transition: background var(--transition-fast);
}

.results-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .results-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .results-actions {
    justify-content: flex-end;
  }
  
  .results-list {
    padding: 12px 16px 16px 16px;
    gap: 8px;
  }
}
</style> 