<!--
  批量操作标签页组件
-->
<template>
  <div class="batch-actions-tab">
    <div class="batch-form">
      <div class="form-group">
        <label class="form-label">
          <i class="fas fa-tag"></i>
          标签操作
        </label>
        <div class="label-input-row">
          <el-select
            v-model="labelInput"
            placeholder="请选择标签"
            size="default"
            filterable
            clearable
            style="flex: 1"
          >
            <el-option
              v-for="option in labelStore.labelOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <ModernButton
            text="添加"
            icon="fas fa-plus"
            :loading="isUpdating"
            :disabled="!labelInput || (!hasSelection && !hasFilterConditions)"
            @click="$emit('addLabels', labelInput)"
          />
          <ModernButton
            text="删除"
            icon="fas fa-minus"
            :loading="isUpdating"
            :disabled="!labelInput || (!hasSelection && !hasFilterConditions)"
            @click="$emit('removeLabels', labelInput)"
          />
        </div>
      </div>

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
  'addLabels': [label: string]
  'removeLabels': [label: string]
  'update:operationMode': [mode: 'selected' | 'filtered']
}

defineEmits<Emits>()

// Store
const labelStore = useLabelStore()

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
.batch-actions-tab {
  padding: 8px 12px;
  height: 100%;
}

.batch-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
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
  padding: var(--spacing-sm);
  background: var(--el-bg-color-page);
  border-radius: var(--radius-md);
  border: 1px solid var(--el-border-color-lighter);
}

.batch-warning {
  margin-top: var(--spacing-sm);
}
</style> 