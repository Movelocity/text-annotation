<!--
  标签条目组件
  功能：显示单个标签的信息、统计数据，支持编辑
-->
<template>
  <div
    class="label-item"
    :class="{ 'edit-mode': editMode, 'clickable': !editMode }"
    @click="handleClick"
  >
    <div class="label-main">
      <!-- 标签名称 -->
      <div class="label-name-section">
        <span class="label-name">{{ label.label }}</span>
        <div class="label-stats" v-if="stats">
          <span class="usage-count">{{ stats.count }} 条数据</span>
          <div class="usage-bar">
            <div 
              class="usage-progress"
              :style="{ width: `${usagePercentage}%` }"
            ></div>
          </div>
        </div>
        <div class="no-stats" v-else>
          <span class="unused-label">未使用</span>
        </div>
      </div>

      <!-- 编辑按钮 -->
      <div class="label-actions" v-if="editMode">
        <el-button
          size="small"
          text
          type="primary"
          @click.stop="showEditDialog = true"
        >
          <i class="fas fa-edit"></i>
        </el-button>
      </div>
    </div>

    <!-- 标签描述 -->
    <div class="label-description" v-if="label.description">
      <span class="description-text">{{ label.description }}</span>
    </div>

    <!-- 标签分组 -->
    <div class="label-group" v-if="label.groups">
      <el-tag size="small" type="info">
        <i class="fas fa-folder"></i>
        {{ label.groups }}
      </el-tag>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="`编辑标签: ${label.label}`"
      width="500px"
      @close="resetEditForm"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标签名称">
          <el-input
            v-model="editForm.label"
            placeholder="输入标签名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            placeholder="输入标签描述（可选）"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="分组">
          <el-input
            v-model="editForm.groups"
            placeholder="输入分组名称（可选）"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import type { LabelResponse, LabelStats, LabelUpdate } from '@/types/api'

// Props
interface Props {
  label: LabelResponse
  stats?: LabelStats | null
  editMode?: boolean
  maxUsageCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  editMode: false,
  maxUsageCount: 100
})

// Emits
interface Emits {
  'click': [label: LabelResponse]
  'edit': [label: LabelResponse, updates: Partial<LabelUpdate>]
}

const emit = defineEmits<Emits>()

// 响应式状态
const showEditDialog = ref(false)
const editForm = reactive({
  label: '',
  description: '',
  groups: ''
})

// 计算属性
const usagePercentage = computed(() => {
  if (!props.stats) return 0
  return Math.min((props.stats.count / props.maxUsageCount) * 100, 100)
})

// 方法
const handleClick = () => {
  if (!props.editMode) {
    emit('click', props.label)
  }
}

const resetEditForm = () => {
  editForm.label = props.label.label
  editForm.description = props.label.description || ''
  editForm.groups = props.label.groups || ''
}

const saveEdit = () => {
  const updates: Partial<LabelUpdate> = {}
  
  if (editForm.label !== props.label.label) {
    updates.label = editForm.label
  }
  
  if (editForm.description !== (props.label.description || '')) {
    updates.description = editForm.description || null
  }
  
  if (editForm.groups !== (props.label.groups || '')) {
    updates.groups = editForm.groups || null
  }

  if (Object.keys(updates).length > 0) {
    emit('edit', props.label, updates)
  }
  
  showEditDialog.value = false
}

// 初始化编辑表单
resetEditForm()
</script>

<style scoped>
.label-item {
  padding: var(--spacing-md);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: var(--el-border-radius-base);
  background: var(--el-bg-color);
  transition: all 0.2s;
}

.label-item.clickable {
  cursor: pointer;
}

.label-item.clickable:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.label-item.edit-mode {
  border-color: var(--el-color-warning);
  background: var(--el-color-warning-light-9);
}

.label-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.label-name-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.label-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.label-stats {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.usage-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  min-width: 60px;
}

.usage-bar {
  flex: 1;
  height: 4px;
  background: var(--el-fill-color-light);
  border-radius: 2px;
  overflow: hidden;
  max-width: 100px;
}

.usage-progress {
  height: 100%;
  background: var(--el-color-primary);
  transition: width 0.3s;
}

.no-stats {
  display: flex;
  align-items: center;
}

.unused-label {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.label-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.label-description {
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--el-border-color-extra-light);
}

.description-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.label-group {
  margin-top: var(--spacing-sm);
  display: flex;
  align-items: center;
}

.label-group .el-tag {
  --el-tag-text-color: var(--el-text-color-secondary);
}

.label-group .el-tag i {
  margin-right: 4px;
}
</style> 