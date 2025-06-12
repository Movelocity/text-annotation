<!--
  标签条目组件
  功能：显示单个标签的信息、统计数据，支持编辑和过滤
-->
<template>
  <div
    class="label-item"
    :class="{ 
      'edit-mode': editMode, 
      'clickable': !editMode,
      'highlighted': isHighlighted,
      'has-usage': !!stats
    }"
    @click="handleClick"
  >
    <!-- 标签信息行 -->
    <div class="label-row">
      <!-- 左侧：标签名称和描述 -->
      <div class="label-main">
        <div class="label-name">{{ label.label }}</div>
        <div class="label-description" v-if="label.description">{{ label.description }}</div>
      </div>

      <!-- 中间：使用统计和分组 -->
      <div class="label-meta">
        <!-- 使用统计 -->
        <div class="usage-info" v-if="stats">
          <span class="usage-count">{{ stats.count }} 条</span>
          <span class="usage-percentage">{{ Math.round(usagePercentage) }}%</span>
        </div>
        <div class="usage-info unused" v-else>
          <span class="unused-label">未使用</span>
        </div>
        
        <!-- 分组信息 -->
        <div class="group-info" v-if="label.groups">
          <el-tag size="small" type="info" effect="plain">{{ label.groups }}</el-tag>
        </div>
      </div>

      <!-- 右侧：操作按钮 -->
      <div class="label-actions">  
        <el-button
          size="small"
          type="warning"
          plain
          circle
          title="编辑标签"
          @click.stop="showEditDialog = true"
        >
          <i class="fas fa-edit"></i>
        </el-button>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="`编辑标签: ${label.label}`"
      width="500px"
      append-to-body
      destroy-on-close
      @close="resetEditForm"
    >
      <el-form :model="editForm" label-width="80px" label-position="top">
        <el-form-item label="标签名称" required>
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
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveEdit">
            <i class="fas fa-save"></i>
            保存
          </el-button>
        </div>
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
  isHighlighted?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editMode: false,
  maxUsageCount: 100,
  isHighlighted: false
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
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-extralight);
  background: var(--el-bg-color);
  transition: all 0.3s ease;
  position: relative;
  border-radius: 6px;
  margin-bottom: 2px;
}

.label-item.clickable {
  cursor: pointer;
}

.label-item.clickable:hover {
  background: var(--el-fill-color-light);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.label-item.edit-mode {
  background: var(--el-color-warning-light-9);
  border: 1px solid var(--el-color-warning-light-6);
  box-shadow: 0 2px 12px rgba(230, 162, 60, 0.15);
}

.label-item.has-usage {
  border-left: 3px solid var(--el-color-primary-light-3);
}

.label-item.highlighted {
  background: linear-gradient(135deg, var(--el-color-success-light-9) 0%, var(--el-color-success-light-8) 100%);
  /* border: 1px solid var(--el-color-success-light-5); */
  border-left: 3px solid var(--el-color-success);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.2);
  transform: translateY(-2px);
  position: relative;
}

.label-item.highlighted .label-name {
  color: var(--el-color-success-dark-2);
  font-weight: 600;
}

.label-item.highlighted .usage-percentage {
  background: var(--el-color-success);
  color: white;
  box-shadow: 0 2px 4px rgba(103, 194, 58, 0.3);
}


.label-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.label-main {
  flex: 1;
  min-width: 0;
}

.label-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  line-height: 1.3;
  word-break: break-word;
}

.label-description {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
  margin: 0;
}

.label-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.usage-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.usage-info.unused {
  color: var(--el-text-color-placeholder);
}

.usage-count {
  color: var(--el-text-color-secondary);
}

.usage-percentage {
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 11px;
}

.unused-label {
  font-size: 12px;
}

.group-info .el-tag {
  font-size: 12px;
}

.label-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.label-actions .el-button {
  width: 28px;
  height: 28px;
  padding: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

.dialog-footer .el-button i {
  margin-right: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .label-row {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .label-meta {
    justify-content: space-between;
  }
  
  .label-actions {
    align-self: flex-end;
  }
}

/* 动画优化 */
@media (prefers-reduced-motion: reduce) {
  .label-item {
    transition: none;
  }
  
  .label-item.clickable:hover {
    transform: none;
  }
  
  .label-item.highlighted {
    transform: none;
  }
}
</style> 