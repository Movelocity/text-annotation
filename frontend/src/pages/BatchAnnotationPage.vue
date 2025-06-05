<!--
  批量标注页面
  主要功能：批量筛选、预览结果、批量标注
-->
<template>
  <div class="batch-annotation-page">
    <!-- 页面头部 -->
    <div class="page-header glass-panel">
      <div class="header-left">
        <div class="header-breadcrumb">
          <i class="fas fa-home"></i>
          <span class="breadcrumb-separator">/</span>
          <span class="current-page">批量标注</span>
        </div>
        <h1 class="page-title">
          <i class="fas fa-layer-group"></i>
          批量标注工具
        </h1>
        <div class="quick-stats" v-if="!state.isLoading">
          <div class="stat-badge total">
            <i class="fas fa-search"></i>
            <span>筛选结果：{{ state.totalCount }} 条</span>
          </div>
          <div class="stat-badge success" v-if="hasSelection">
            <i class="fas fa-check-square"></i>
            <span>已选择：{{ selectedTextsCount }} 条</span>
          </div>
          <div class="stat-badge info" v-if="state.isPreviewMode">
            <i class="fas fa-eye"></i>
            <span>预览模式</span>
          </div>
        </div>
      </div>
      <div class="header-right">
        <ModernButton
          text="重置"
          icon="fas fa-undo"
          @click="resetState"
        />
        <ModernButton
          text="返回首页"
          icon="fas fa-home"
          @click="goToHome"
        />
      </div>
    </div>

    <!-- 主工作区域 -->
    <div class="work-area">
      <!-- 左侧：筛选条件设置 -->
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
      </div>

      <!-- 右侧：筛选结果和批量操作 -->
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useBatchAnnotation } from '../composables/useBatchAnnotation'
import ModernButton from '../components/common/ModernButton.vue'
import FilterPanel from '../components/batch/FilterPanel.vue'
import ResultsList from '../components/batch/ResultsList.vue'
import BatchActions from '../components/batch/BatchActions.vue'

// Router
const router = useRouter()

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

// 方法
const goToHome = () => {
  router.push('/home')
}

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
  padding: var(--spacing-lg);
  min-height: 100vh;
  background: var(--el-bg-color-page);
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
}

.header-left {
  flex: 1;
}

.header-breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.breadcrumb-separator {
  color: var(--el-text-color-placeholder);
}

.current-page {
  color: var(--el-color-primary);
  font-weight: 500;
}

.page-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin: 0 0 var(--spacing-md) 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.quick-stats {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}

.stat-badge.total {
  background: var(--el-color-info-light-9);
  border-color: var(--el-color-info-light-7);
  color: var(--el-color-info);
}

.stat-badge.success {
  background: var(--el-color-success-light-9);
  border-color: var(--el-color-success-light-7);
  color: var(--el-color-success);
}

.stat-badge.info {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
  color: var(--el-color-primary);
}

.header-right {
  display: flex;
  gap: var(--spacing-md);
}

/* 工作区域 */
.work-area {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: var(--spacing-lg);
  height: calc(100vh - 200px);
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
