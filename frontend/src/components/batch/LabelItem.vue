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
    <!-- 主要内容区域 -->
    <div class="label-content">
      <!-- 标签头部：名称和操作 -->
      <div class="label-header">
        <div class="label-info">
          <h3 class="label-name">{{ label.label }}</h3>
          <div class="label-meta">
            <!-- 使用统计 -->
            <div class="usage-info" v-if="stats">
              <span class="usage-count">
                <i class="fas fa-chart-bar"></i>
                {{ stats.count }} 条数据
              </span>
              <span class="usage-percentage">{{ Math.round(usagePercentage) }}%</span>
            </div>
            <div class="usage-info unused" v-else>
              <span class="unused-label">
                <i class="fas fa-circle"></i>
                未使用
              </span>
            </div>
            
            <!-- 分组信息 -->
            <div class="group-info" v-if="label.groups">
              <el-tag size="small" type="info" effect="light">
                <i class="fas fa-folder"></i>
                {{ label.groups }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
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

      <!-- 使用进度条 -->
      <div v-if="stats">
        <div class="usage-bar">
          <div 
            class="usage-progress"
            :style="{ width: `${usagePercentage}%` }"
            :class="getUsageClass()"
          ></div>
        </div>
      </div>

      <!-- 标签描述 -->
      <div class="label-description">
        <p class="description-text" v-if="label.description">
          <i class="fas fa-info-circle"></i>
          {{ label.description }}
        </p>
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

const getUsageClass = () => {
  const percentage = usagePercentage.value
  if (percentage >= 80) return 'high-usage'
  if (percentage >= 40) return 'medium-usage'
  return 'low-usage'
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
  padding: 0;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-bg-color);
  transition: all 0.2s ease-in-out;
  position: relative;
  overflow: hidden;
}

.label-item.clickable {
  cursor: pointer;
}

.label-item.clickable:hover {
  /* border-color: var(--el-color-primary); */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translate(0, -4px);
}

.label-item.edit-mode {
  border-color: var(--el-color-warning);
  background: var(--el-color-warning-light-9);
}

.label-item.highlighted {
  /* border-color: var(--el-color-success); */
  background: var(--el-color-success-light-9);
  /* box-shadow: 0 0 0 2px var(--el-color-success-light-7); */
  /* transform: translateY(-1px); */
}

.label-item.has-usage {
  border-left: 4px solid var(--el-color-primary-light-3);
}

/* .label-item.has-usage.highlighted {
  border-left-color: var(--el-color-success);
} */

.label-content {
  padding: var(--spacing-lg);
}

.label-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.label-info {
  flex: 1;
  min-width: 0;
}

.label-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 var(--spacing-sm) 0;
  line-height: 1.3;
  word-break: break-word;
}

.label-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-md);
}

.usage-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.usage-info.unused {
  color: var(--el-text-color-placeholder);
}

.usage-info i {
  font-size: 12px;
  opacity: 0.7;
}

.usage-count {
  display: flex;
  align-items: center;
  gap: 4px;
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
  display: flex;
  align-items: center;
  gap: 4px;
}

.group-info .el-tag {
  font-size: 12px;
}

.group-info .el-tag i {
  margin-right: 4px;
  font-size: 11px;
}

.label-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

.label-actions .el-button {
  width: 32px;
  height: 32px;
  padding: 0;
}

.usage-bar {
  height: 6px;
  background: var(--el-border-color-lighter);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.usage-progress {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease-in-out;
  position: relative;
}

.usage-progress.low-usage {
  background: linear-gradient(90deg, var(--el-color-info) 0%, var(--el-color-primary-light-3) 100%);
}

.usage-progress.medium-usage {
  background: linear-gradient(90deg, var(--el-color-warning) 0%, var(--el-color-primary) 100%);
}

.usage-progress.high-usage {
  background: linear-gradient(90deg, var(--el-color-success) 0%, var(--el-color-primary) 100%);
}

.label-description {
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--el-border-color-extralight);
}

.description-text {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-xs);
}

.description-text i {
  color: var(--el-color-info);
  margin-top: 2px;
  flex-shrink: 0;
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
  .label-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }
  
  .label-actions {
    justify-content: flex-end;
  }
  
  .label-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .label-name {
    font-size: 16px;
  }
}

/* 无障碍支持 */
/* .label-item:focus-within {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
} */

/* 动画优化 */
@media (prefers-reduced-motion: reduce) {
  .label-item,
  .usage-progress {
    transition: none;
  }
  
  .label-item.highlighted {
    animation: none;
  }
}
</style> 