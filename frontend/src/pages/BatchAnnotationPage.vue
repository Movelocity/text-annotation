<!--
  批量标注页面
  主要功能：批量筛选、预览结果、批量标注
-->
<template>
  <div class="batch-annotation-page">
    <!-- 页面头部 -->
    <PageHeader
      title="批量标注工具"
      title-icon="fas fa-layer-group"
      :breadcrumbs="breadcrumbs"
      :stats="headerStats"
      home-route="/home"
    >
      <template #actions>
        <ModernButton
          text="重置"
          icon="fas fa-undo"
          @click="resetState"
        />
      </template>
    </PageHeader>

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
          @update:include-keywords="setIncludeKeywords"
          @update:exclude-keywords="setExcludeKeywords"
          @update:include-labels="setIncludeLabels"
          @update:exclude-labels="setExcludeLabels"
          @update:unlabeled-only="setUnlabeledOnly"
          @preview="previewFilter"
          @filter="filterTexts"
        />

        <!-- 批量操作 -->
        <BatchActions
          v-if="state.filteredTexts.length > 0"
          :selected-texts-count="selectedTextsCount"
          :total-count="state.totalCount"
          :filtered-count="state.filteredTexts.length"
          :has-selection="hasSelection"
          :has-filter-conditions="hasFilterConditions"
          :is-updating="state.isUpdating"
          v-model:operation-mode="operationMode"
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
          @select-all="selectAll"
          @clear-selection="clearSelection"
          @toggle-selection="toggleSelection"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useBatchAnnotation } from '@/composables/useBatchAnnotation'
import ModernButton from '@/components/common/ModernButton.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterPanel from '@/components/batch/FilterPanel.vue'
import ResultsList from '@/components/batch/ResultsList.vue'
import BatchActions from '@/components/batch/BatchActions.vue'


// Composable
const {
  state,
  hasFilterConditions,
  selectedTextsCount,
  hasSelection,
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
  resetState,
  setIncludeKeywords,
  setExcludeKeywords,
  setIncludeLabels,
  setExcludeLabels,
  setUnlabeledOnly
} = useBatchAnnotation()

const operationMode = ref<'selected' | 'filtered'>('selected')

// 面包屑导航配置
const breadcrumbs = [
  { text: '批量标注' }
]

// 定义统计项类型
interface StatItem {
  key: string
  label: string
  value: string | number
  type?: 'total' | 'success' | 'warning' | 'primary' | 'info' | 'danger' | 'default'
  icon?: string
}

// 头部统计信息
const headerStats = computed<StatItem[]>(() => {
  if (state.isLoading) return []
  
  const stats: StatItem[] = [
    {
      key: 'filtered',
      label: '筛选结果',
      value: `${state.totalCount} 条`,
      type: 'total',
      icon: 'fas fa-search'
    }
  ]
  
  // 如果有选择，添加已选择信息
  if (hasSelection.value) {
    stats.push({
      key: 'selected',
      label: '已选择',
      value: `${selectedTextsCount.value} 条`,
      type: 'success',
      icon: 'fas fa-check-square'
    })
  }
  
  // 如果是预览模式，添加预览标识
  if (state.isPreviewMode) {
    stats.push({
      key: 'preview',
      label: '预览模式',
      value: '',
      type: 'info',
      icon: 'fas fa-eye'
    })
  }
  
  return stats
})

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
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}



/* 工作区域 */
.work-area {
  flex: 1;
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 16px;
  padding: 0 16px 16px;
  min-height: 0;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
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
    height: auto;
  }
  
  .page-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
