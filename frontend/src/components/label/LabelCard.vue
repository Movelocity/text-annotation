<template>
  <el-card class="label-card" :class="{ 'unused': isUnused }" @click="handleCardClick">
    <!-- 主要信息：始终显示 -->
    <div class="label-main">
      <div class="label-info">
        <div class="label-header">
          <div class="label-name">{{ label.label }}</div>
          <div v-if="label.groups" class="label-group">
            <el-tag size="small" type="info" plain>
              <el-icon><Folder /></el-icon>
              {{ label.groups }}
            </el-tag>
          </div>
        </div>
        <div v-if="label.description" class="label-description">
          {{ label.description }}
        </div>
      </div>
      <div class="label-status">
        <el-tag :type="isUnused ? 'warning' : 'success'" size="small">
          {{ usageCount }}次
        </el-tag>
      </div>
    </div>

    <!-- 次要信息：默认展开 -->
    <div class="label-details">
      <div class="label-meta">
        <span class="label-id">ID: {{ label.id }}</span>
        <el-dropdown @command="handleCommand" @click.stop>
          <el-button type="text" class="action-btn" size="small">
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="edit">
                <el-icon><Edit /></el-icon>
                编辑标签
              </el-dropdown-item>
              <el-dropdown-item command="delete" class="delete-item">
                <el-icon><Delete /></el-icon>
                删除标签
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div v-if="!isUnused" class="usage-indicator">
        <div class="usage-bar-mini">
          <div class="usage-fill" :style="{ width: `${usagePercentage}%`, backgroundColor: progressColor }"></div>
        </div>
        <span class="usage-text">{{ usagePercentage }}%</span>
      </div>

      <div class="label-actions">
        <el-button 
          type="primary" 
          size="small" 
          @click.stop="handleViewUsage"
          :disabled="isUnused"
          plain
        >
          查看详情
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { MoreFilled, Delete, Edit, Folder } from '@element-plus/icons-vue'
import type { LabelResponse, LabelStats } from '@/types/api'

interface Props {
  label: LabelResponse
  stats: LabelStats | null
  maxUsageCount?: number // 所有标签中的最大使用次数，用于计算相对百分比
}

interface Emits {
  (e: 'delete', label: LabelResponse): void
  (e: 'edit', label: LabelResponse): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 计算属性
const usageCount = computed(() => props.stats?.count || 0)
const isUnused = computed(() => usageCount.value === 0)

// 优化后的百分比计算
const usagePercentage = computed(() => {
  if (isUnused.value) return 0
  
  // 如果传入了最大使用次数，则基于此计算相对百分比
  if (props.maxUsageCount && props.maxUsageCount > 0) {
    return Math.round((usageCount.value / props.maxUsageCount) * 100)
  }
  
  // 备用计算方式：基于一个合理的基准值
  // 如果使用次数小于10，基准为20；如果小于50，基准为100；否则基准为使用次数的1.5倍
  let baseCount: number
  if (usageCount.value <= 10) {
    baseCount = 20
  } else if (usageCount.value <= 50) {
    baseCount = 100
  } else {
    baseCount = Math.ceil(usageCount.value * 1.5)
  }
  
  return Math.min(Math.round((usageCount.value / baseCount) * 100), 100)
})

const progressColor = computed(() => {
  const percentage = usagePercentage.value
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  if (percentage >= 20) return '#f56c6c'
  return '#909399'
})

// 方法
const handleCommand = (command: string) => {
  if (command === 'delete') {
    emit('delete', props.label)
  } else if (command === 'edit') {
    emit('edit', props.label)
  }
}

const handleViewUsage = () => {
  if (isUnused.value) {
    ElMessage.info('该标签暂未被使用')
    return
  }
  
  // 这里可以跳转到标注页面并筛选该标签
  ElMessage.info('功能开发中：查看标签使用详情')
}

const handleCardClick = () => {
  // 点击卡片的默认行为，可以用于快速选择或预览
  console.log('Label card clicked:', props.label.label)
}
</script>

<style scoped>
.label-card {
  border: none;
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.25s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
}

.label-card:hover {
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.label-card.unused {
  border-left: 3px solid #e6a23c;
}

/* .label-card:not(.unused) {
  border-left: 3px solid #67c23a;
} */

/* 主要信息区域 */
.label-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.label-info {
  flex: 1;
  margin-right: 12px;
}

.label-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 6px;
}

.label-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  word-break: break-all;
}

.label-group {
  align-self: flex-start;
}

.label-description {
  font-size: 13px;
  color: #909399;
  line-height: 1.4;
  word-break: break-all;
}

.label-status {
  flex-shrink: 0;
}

/* 次要信息区域：默认展开 */
.label-details {
  opacity: 1;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  transition: all 0.25s ease;
}

.label-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.label-id {
  font-size: 11px;
  color: #c0c4cc;
}

.action-btn {
  padding: 2px 4px;
  color: #c0c4cc;
  opacity: 0.7;
}

.action-btn:hover {
  color: #409eff;
  opacity: 1;
}

.delete-item {
  color: #f56c6c;
}

/* 简化的使用率指示器 */
.usage-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.usage-bar-mini {
  flex: 1;
  height: 3px;
  background-color: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 2px;
}

.usage-text {
  font-size: 11px;
  color: #909399;
  min-width: 30px;
  text-align: right;
}

.label-actions {
  text-align: right;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .label-name {
    font-size: 14px;
  }
  
  .label-main {
    margin-bottom: 8px;
  }
  
  .label-details {
    padding-top: 8px;
  }
}
</style> 