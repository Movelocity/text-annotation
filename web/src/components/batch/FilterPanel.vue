<!--
  筛选条件面板组件
-->
<template>
  <div class="filter-panel glass-panel">

    <!-- Tab 标签页 -->
    <el-tabs v-model="activeTab" class="filter-tabs">
      <!-- 标签管理 Tab -->
      <el-tab-pane label="标签管理" name="labels">
        <template #label>
          <span class="tab-label">
            <i class="fas fa-tags"></i>
            标签管理
          </span>
        </template>
        
        <LabelManagementTab 
          :current-filter-label="getCurrentFilterLabel ?? ''" 
          @label-selected="handleLabelSelected" 
        />
      </el-tab-pane>

      <!-- 筛选条件 Tab -->
      <el-tab-pane label="筛选条件" name="filter">
        <template #label>
          <span class="tab-label">
            <i class="fas fa-filter"></i>
            筛选条件
          </span>
        </template>
        
        <FilterConditionsTab
          :include-keywords="includeKeywords"
          :exclude-keywords="excludeKeywords"
          :include-labels="includeLabels"
          :exclude-labels="excludeLabels"
          :unlabeled-only="unlabeledOnly"
          :is-loading="isLoading"
          @update:include-keywords="$emit('update:includeKeywords', $event)"
          @update:exclude-keywords="$emit('update:excludeKeywords', $event)"
          @update:include-labels="$emit('update:includeLabels', $event)"
          @update:exclude-labels="$emit('update:excludeLabels', $event)"
          @update:unlabeled-only="$emit('update:unlabeledOnly', $event)"
          @preview="$emit('preview')"
          @filter="$emit('filter')"
        />
      </el-tab-pane>

      <!-- 批量操作 Tab -->
      <el-tab-pane label="批量操作" name="batch">
        <template #label>
          <span class="tab-label">
            <i class="fas fa-magic"></i>
            批量操作
          </span>
        </template>
        
        <BatchActionsTab
          :selected-texts-count="selectedTextsCount"
          :total-count="totalCount"
          :filtered-count="filteredCount"
          :has-selection="hasSelection"
          :has-filter-conditions="hasFilterConditions"
          :is-updating="isUpdating"
          :operation-mode="operationMode"
          @add-labels="$emit('addLabels', $event)"
          @remove-labels="$emit('removeLabels', $event)"
          @update:operation-mode="$emit('update:operationMode', $event)"
        />
      </el-tab-pane>

      
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from 'vue'
import { useLabelStore } from '@/stores/label'
import LabelManagementTab from './LabelManagementTab.vue'
import FilterConditionsTab from './FilterConditionsTab.vue'
import BatchActionsTab from './BatchActionsTab.vue'

// Props
interface Props {
  includeKeywords: string[]
  excludeKeywords: string[]
  includeLabels: string[]
  excludeLabels: string[]
  unlabeledOnly: boolean
  isLoading: boolean
  // BatchActions 相关 props
  selectedTextsCount: number
  totalCount: number
  filteredCount: number
  hasSelection: boolean
  hasFilterConditions: boolean
  isUpdating: boolean
  operationMode: 'selected' | 'filtered'
}

const props = withDefaults(defineProps<Props>(), {
  includeKeywords: () => [],
  excludeKeywords: () => [],
  includeLabels: () => [],
  excludeLabels: () => [],
  unlabeledOnly: false,
  isLoading: false,
  selectedTextsCount: 0,
  totalCount: 0,
  filteredCount: 0,
  hasSelection: false,
  hasFilterConditions: false,
  isUpdating: false,
  operationMode: 'selected'
})

// Emits
interface Emits {
  'update:includeKeywords': [keywords: string[]]
  'update:excludeKeywords': [keywords: string[]]
  'update:includeLabels': [labels: string[]]
  'update:excludeLabels': [labels: string[]]
  'update:unlabeledOnly': [unlabeledOnly: boolean]
  'preview': []
  'filter': []
  // BatchActions 相关 emits
  'addLabels': [labels: string[]]
  'removeLabels': [labels: string[]]
  'update:operationMode': [mode: 'selected' | 'filtered']
}

const emit = defineEmits<Emits>()

// Store
const labelStore = useLabelStore()

// 响应式状态
const activeTab = ref('labels')

// 获取当前筛选的标签（用于标签管理Tab的选中状态）
const getCurrentFilterLabel = computed(() => {
  // 如果只有一个包含标签且没有其他筛选条件，则返回该标签
  if (props.includeLabels.length === 1 && 
      props.excludeLabels.length === 0 && 
      props.includeKeywords.length === 0 && 
      props.excludeKeywords.length === 0 && 
      !props.unlabeledOnly) {
    return props.includeLabels[0]
  }
  return null
})

// 标签选择处理
const handleLabelSelected = async (label: string) => {
  // 如果当前已经选中这个标签，则清除所有筛选条件
  if (props.includeLabels.length === 1 && props.includeLabels[0] === label) {
    emit('update:includeKeywords', [])
    emit('update:excludeKeywords', [])
    emit('update:includeLabels', [])
    emit('update:excludeLabels', [])
    emit('update:unlabeledOnly', false)
  } else {
    // 否则清除所有筛选条件，只保留这个选中的标签作为唯一筛选条件
    emit('update:includeKeywords', [])
    emit('update:excludeKeywords', [])
    emit('update:includeLabels', [label])
    emit('update:excludeLabels', [])
    emit('update:unlabeledOnly', false)
  }
  console.log('handleLabelSelected', label)
  // 不跳转tab，保持在标签管理页面
  // 等待 props 更新完成后再执行筛选
  await nextTick()
  // 筛选逻辑现在由FilterConditionsTab处理
  emit('filter')
}

// 生命周期
onMounted(async () => {
  // 初始化标签数据
  if (!labelStore.hasLabels) {
    await labelStore.fetchLabels()
  }
})
</script>

<style scoped>
.filter-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-tabs {
  height: 100%;
  display: flex;
}

.filter-tabs :deep(.el-tabs__header) {
  flex-shrink: 0;
  margin-bottom: 8px;
  padding: 0 12px;
}

.filter-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

.filter-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow-y: auto;
  padding: 0 4px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
</style> 