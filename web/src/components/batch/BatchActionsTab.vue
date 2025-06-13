<!--
  批量操作标签页组件
-->
<template>
  <div class="batch-actions-tab">
    <!-- 操作模式 -->
    <div class="operation-mode">
      <el-radio-group 
        :model-value="operationMode" 
        @update:model-value="$emit('update:operationMode', $event)"
        size="default"
      >
        <el-radio value="selected" :disabled="!hasSelection">
          仅选中的文本 ({{ selectedTextsCount }} 条)
        </el-radio>
        <el-radio value="filtered" :disabled="!hasFilterConditions">
          所有筛选结果 ({{ totalCount }} 条)
        </el-radio>
      </el-radio-group>
    </div>

    <!-- 操作区域 -->
    <div class="action-area">
      <div class="action-buttons">
        <el-button
          :disabled="selectedLabels.length === 0 || (!hasSelection && !hasFilterConditions)"
          type="danger"
          size="default"
          text
          @click="handleClearAllLabels"
          class="clear-all-btn"
        >
          清除选择
        </el-button>
        <ModernButton
          text="删除标签"
          icon="fas fa-minus"
          :loading="isUpdating"
          :disabled="selectedLabels.length === 0 || (!hasSelection && !hasFilterConditions)"
          @click="handleBatchRemove"
        />
        <ModernButton
          text="添加标签"
          icon="fas fa-plus"
          :loading="isUpdating"
          :disabled="selectedLabels.length === 0 || (!hasSelection && !hasFilterConditions)"
          @click="handleBatchAdd"
        />
      </div>
      
    </div>

    <!-- 标签选择区域 -->
    <div class="label-selection">
      <div class="search-header">
        <el-input
          v-model="labelSearch"
          placeholder="搜索标签..."
          clearable
          prefix-icon="Search"
          size="default"
        />
        <span class="selection-count" v-if="selectedLabels.length > 0">
          已选择 {{ selectedLabels.length }} 个
        </span>
      </div>

      <!-- 标签网格选择 -->
      <div class="labels-container" v-loading="labelStore.loading">
        <div v-if="!labelStore.hasLabels && !labelStore.loading" class="empty-labels">
          <el-empty description="暂无标签" />
        </div>
        
        <div v-else class="labels-grid">
          <div
            v-for="label in filteredLabels"
            :key="label.value"
            class="label-item"
            :class="{ 
              'selected': selectedLabels.includes(label.value)
            }"
            @click="handleLabelToggle(label.value)"
          >
            <div class="label-content">
              <span class="label-text">{{ label.label }}</span>
              <i v-if="selectedLabels.includes(label.value)" class="fas fa-check selected-icon"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="action-preview" v-if="selectedLabels.length > 0">
        <div class="preview-text">
          将对 {{ targetCount }} 条文本执行标签操作
        </div>
        <div class="selected-labels-preview">
          <el-tag
            v-for="(labelValue, _index) in selectedLabels.slice(0, 3)"
            :key="labelValue"
            size="small"
            type="info"
          >
            {{ getLabelText(labelValue) }}
          </el-tag>
          <span v-if="selectedLabels.length > 3" class="more-count">
            +{{ selectedLabels.length - 3 }}
          </span>
        </div>
      </div>
    </div>



    <!-- 批量操作警告 -->
    <div class="batch-warning" v-if="operationMode === 'filtered' && totalCount > filteredCount">
      <el-alert
        type="warning"
        show-icon
        :closable="false"
      >
        <template #title>
          将对所有 {{ totalCount }} 条筛选结果执行操作，包括未显示的数据
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useLabelStore } from '@/stores/label'
import ModernButton from '../common/ModernButton.vue'

// Props
interface Props {
  selectedTextsCount: number
  totalCount: number
  filteredCount: number
  hasSelection: boolean
  hasFilterConditions: boolean
  isUpdating: boolean
  operationMode: 'selected' | 'filtered'
}

const props = defineProps<Props>()

// Emits
interface Emits {
  'addLabels': [labels: string[]]
  'removeLabels': [labels: string[]]
  'update:operationMode': [mode: 'selected' | 'filtered']
}

const emit = defineEmits<Emits>()

// Store
const labelStore = useLabelStore()

// 响应式数据
const selectedLabels = ref<string[]>([])
const labelSearch = ref('')

// 计算属性
const filteredLabels = computed(() => {
  if (!labelSearch.value) return labelStore.labelOptions
  return labelStore.labelOptions.filter(option => 
    option.label.toLowerCase().includes(labelSearch.value.toLowerCase())
  )
})

const targetCount = computed(() => {
  return props.operationMode === 'selected' ? props.selectedTextsCount : props.totalCount
})

// 方法
const handleLabelToggle = (labelValue: string) => {
  const index = selectedLabels.value.indexOf(labelValue)
  if (index > -1) {
    selectedLabels.value.splice(index, 1)
  } else {
    selectedLabels.value.push(labelValue)
  }
}

const handleClearAllLabels = () => {
  selectedLabels.value = []
}

const getLabelText = (labelValue: string) => {
  const option = labelStore.labelOptions.find(opt => opt.value === labelValue)
  return option ? option.label : labelValue
}

const handleBatchAdd = () => {
  if (selectedLabels.value.length > 0) {
    emit('addLabels', [...selectedLabels.value])
  }
}

const handleBatchRemove = () => {
  if (selectedLabels.value.length > 0) {
    emit('removeLabels', [...selectedLabels.value])
  }
}

// 监听操作完成，清空选择
watch(() => props.isUpdating, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    // 从loading变为非loading状态，说明操作完成
    selectedLabels.value = []
  }
})
</script>

<style scoped>
.batch-actions-tab {
  padding: 16px;
  height: 95%;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.operation-mode {
  margin-bottom: 4px;
}

.label-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.search-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selection-count {
  font-size: 13px;
  color: var(--el-color-primary);
  font-weight: 500;
  white-space: nowrap;
}

.labels-container {
  flex: 1;
  min-height: 0;
}

.empty-labels {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.labels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
  height: 100%;
  overflow-y: auto;
  padding: 4px;
}

.label-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: var(--el-bg-color);
}

.label-item:hover {
  border-color: var(--el-color-primary-light-3);
  background: var(--el-fill-color-extra-light);
}

.label-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.label-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.label-text {
  font-size: 13px;
  word-break: break-word;
  flex: 1;
  line-height: 1.4;
}

.selected-icon {
  font-size: 12px;
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.batch-warning {
  margin: 4px 0;
}

.action-area {
  /* flex-shrink: 0; */
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-preview {
  padding: 12px;
  background: var(--el-fill-color-extra-light);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
}

.preview-text {
  font-size: 13px;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.selected-labels-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.more-count {
  color: var(--el-text-color-regular);
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.clear-all-btn {
  font-size: 13px;
  margin-left: auto;
}
</style> 