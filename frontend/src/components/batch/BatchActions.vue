<!--
  批量操作面板组件
-->
<template>
  <div class="batch-actions-panel glass-panel">
    <div class="section-header">
      <h2>
        <i class="fas fa-magic"></i>
        批量操作
      </h2>
    </div>

    <div class="batch-form">
      <div class="form-group">
        <label class="form-label">
          <i class="fas fa-tag"></i>
          标签操作
        </label>
        <div class="label-input-row">
          <el-input
            v-model="labelInput"
            placeholder="输入要添加或删除的标签"
            size="small"
          />
          <el-button
            type="success"
            size="small"
            :loading="isUpdating"
            :disabled="!labelInput.trim() || (!hasSelection && !hasFilterConditions)"
            @click="$emit('addLabels', labelInput.trim())"
          >
            <i class="fas fa-plus"></i>
            添加
          </el-button>
          <el-button
            type="danger"
            size="small"
            :loading="isUpdating"
            :disabled="!labelInput.trim() || (!hasSelection && !hasFilterConditions)"
            @click="$emit('removeLabels', labelInput.trim())"
          >
            <i class="fas fa-minus"></i>
            删除
          </el-button>
        </div>
      </div>

      <div class="operation-mode">
        <el-radio-group 
          :model-value="operationMode" 
          @update:model-value="$emit('update:operationMode', $event)"
          size="small"
        >
          <el-radio value="selected" :disabled="!hasSelection">
            仅选中的文本 ({{ selectedTextsCount }} 条)
          </el-radio>
          <el-radio value="filtered" :disabled="!hasFilterConditions">
            所有筛选结果 ({{ totalCount }} 条)
          </el-radio>
        </el-radio-group>
      </div>

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
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

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
  'addLabels': [label: string]
  'removeLabels': [label: string]
  'update:operationMode': [mode: 'selected' | 'filtered']
}

const emit = defineEmits<Emits>()

// 表单数据
const labelInput = ref('')

// 监听操作完成，清空输入框
watch(() => props.isUpdating, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    // 从loading变为非loading状态，说明操作完成
    labelInput.value = ''
  }
})
</script>

<style scoped>
.batch-actions-panel {
  padding: var(--spacing-xl);
  height: fit-content;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
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

.batch-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.label-input-row {
  display: flex;
  gap: var(--spacing-sm);
}

.label-input-row .el-input {
  flex: 1;
}

.operation-mode {
  padding: var(--spacing-md);
  background: var(--el-bg-color-page);
  border-radius: var(--radius-md);
  border: 1px solid var(--el-border-color-lighter);
}

.batch-warning {
  margin-top: var(--spacing-md);
}
</style> 