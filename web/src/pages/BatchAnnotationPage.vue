<!--
  批量标注页面
  主要功能：批量筛选、预览结果、批量标注
-->
<template>
  <div class="batch-annotation-page">
    <!-- 主工作区域 -->
    <div class="work-area">
      <!-- 左侧：筛选条件设置和批量操作 -->
      <div class="left-panel">
        <FilterPanel
          :include-keywords="state.filterOptions.includeKeywords ?? []"
          :exclude-keywords="state.filterOptions.excludeKeywords ?? []"
          :include-labels="state.filterOptions.includeLabels ?? []"
          :exclude-labels="state.filterOptions.excludeLabels ?? []"
          :unlabeled-only="state.filterOptions.unlabeledOnly ?? false"
          :is-loading="state.isLoading"
          :selected-texts-count="selectedTextsCount"
          :total-count="state.totalCount"
          :filtered-count="state.filteredTexts.length"
          :has-selection="hasSelection"
          :has-filter-conditions="hasFilterConditions"
          :is-updating="state.isUpdating"
          :operation-mode="operationMode"
          @update:include-keywords="setIncludeKeywords"
          @update:exclude-keywords="setExcludeKeywords"
          @update:include-labels="setIncludeLabels"
          @update:exclude-labels="setExcludeLabels"
          @update:unlabeled-only="setUnlabeledOnly"
          @update:operation-mode="operationMode = $event"
          @preview="previewFilter"
          @filter="() => filterTexts(true)"
          @add-labels="handleAddLabels"
          @remove-labels="handleRemoveLabels"
        />
      </div>

      <!-- 右侧：筛选结果 -->
      <div class="right-panel">
        <!-- 筛选结果 -->
        <ResultsList
          :filtered-texts="state.filteredTexts"
          :total-count="state.totalCount"
          :selected-texts-count="selectedTextsCount"
          :is-loading="state.isLoading"
          :has-filter-conditions="hasFilterConditions"
          :is-selected="isSelected"
          :keywords="state.filterOptions.includeKeywords ?? []"
          @select-all="selectAll"
          @clear-selection="clearSelection"
          @toggle-selection="toggleSelection"
        />

        <!-- 分页组件 -->
        <div class="pagination-section" v-if="state.filteredTexts.length > 0">
          <Pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="state.totalCount"
            :disabled="state.isLoading"
            @page-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useBatchAnnotation } from '@/composables/useBatchAnnotation'
import FilterPanel from '@/components/batch/FilterPanel.vue'
import ResultsList from '@/components/batch/ResultsList.vue'
import Pagination from '@/components/common/Pagination.vue'


// Composable
const {
  state,
  hasFilterConditions,
  selectedTextsCount,
  hasSelection,
  currentPage,
  pageSize,
  // totalPages,
  filterTexts,
  previewFilter,
  addLabelsToFiltered,
  removeLabelsFromFiltered,
  addLabelsToSelected,
  removeLabelsFromSelected,
  selectAll,
  clearSelection,
  toggleSelection,
  isSelected,
  handlePageChange,
  handlePageSizeChange,
  setIncludeKeywords,
  setExcludeKeywords,
  setIncludeLabels,
  setExcludeLabels,
  setUnlabeledOnly
} = useBatchAnnotation()

const operationMode = ref<'selected' | 'filtered'>('selected')

// 批量操作
const handleAddLabels = async (label: string) => {
  if (!label) return

  try {
    await ElMessageBox.confirm(
      `确定要${operationMode.value === 'selected' ? '为选中的' : '为所有筛选结果的'} ${operationMode.value === 'selected' ? selectedTextsCount.value : state.totalCount} 条文本添加标签 "${label}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    if (operationMode.value === 'selected') {
      await addLabelsToSelected([label])
    } else {
      await addLabelsToFiltered([label])
    }
  } catch {
    // 用户取消
  }
}

const handleRemoveLabels = async (label: string) => {
  if (!label) return

  try {
    await ElMessageBox.confirm(
      `确定要从${operationMode.value === 'selected' ? '选中的' : '所有筛选结果的'} ${operationMode.value === 'selected' ? selectedTextsCount.value : state.totalCount} 条文本中删除标签 "${label}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    if (operationMode.value === 'selected') {
      await removeLabelsFromSelected([label])
    } else {
      await removeLabelsFromFiltered([label])
    }
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.batch-annotation-page {
  height: calc(100vh - 55px);
  display: flex;
  flex-direction: column;
  /* background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); */
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  background: #fff;
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title i {
  color: var(--el-color-primary);
}

.header-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-shrink: 0;
}

/* 工作区域 */
.work-area {
  flex: 1;
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 16px;
  padding: 16px;
  min-height: 0;
  overflow: hidden;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  min-height: 0;
  overflow: hidden;
}

.left-panel {
  padding-bottom: 16px;
}

.right-panel {
  height: 100%;
}

/* 分页区域 */
.pagination-section {
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

/* 删除了已移到子组件的样式 */

/* 响应式设计 */
@media (max-width: 1200px) {
  .work-area {
    grid-template-columns: 350px 1fr;
  }
}

@media (max-width: 768px) {
  .work-area {
    grid-template-columns: 1fr;
    overflow: auto;
  }
  
  .left-panel, .right-panel {
    overflow: visible;
    height: auto;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
