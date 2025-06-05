<template>
  <el-card class="label-card" :class="{ 'unused': isUnused }">
    <div class="label-header">
      <div class="label-info">
        <div class="label-name">{{ label.label }}</div>
        <div class="label-id">ID: {{ label.id }}</div>
      </div>
      <div class="label-actions">
        <el-dropdown @command="handleCommand">
          <el-button type="text" class="action-btn">
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="delete" class="delete-item">
                <el-icon><Delete /></el-icon>
                删除标签
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="label-stats">
      <div class="stat-item">
        <div class="stat-label">使用次数</div>
        <div class="stat-value" :class="{ 'zero': usageCount === 0 }">
          {{ usageCount }}
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">状态</div>
        <el-tag :type="isUnused ? 'warning' : 'success'" size="small">
          {{ isUnused ? '未使用' : '已使用' }}
        </el-tag>
      </div>
    </div>

    <div v-if="!isUnused" class="usage-bar">
      <div class="usage-bar-label">使用频率</div>
      <el-progress 
        :percentage="usagePercentage" 
        :stroke-width="6"
        :show-text="false"
        :color="progressColor"
      />
      <div class="usage-bar-text">{{ usagePercentage }}%</div>
    </div>

    <div class="label-footer">
      <el-button 
        type="primary" 
        size="small" 
        @click="handleViewUsage"
        :disabled="isUnused"
      >
        查看使用详情
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { MoreFilled, Delete } from '@element-plus/icons-vue'
import type { LabelResponse, LabelStats } from '@/types/api'

interface Props {
  label: LabelResponse
  stats: LabelStats | null
}

interface Emits {
  (e: 'delete', label: LabelResponse): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 计算属性
const usageCount = computed(() => props.stats?.count || 0)
const isUnused = computed(() => usageCount.value === 0)

// 计算使用百分比（相对于最高使用量）
const usagePercentage = computed(() => {
  if (isUnused.value) return 0
  // 这里可以传入最大使用量来计算相对百分比
  // 暂时使用简单的计算方式
  const maxCount = Math.max(usageCount.value, 100) // 假设最大值为100或当前值
  return Math.round((usageCount.value / maxCount) * 100)
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
</script>

<style scoped>
.label-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.label-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.label-card.unused {
  border-left: 4px solid #e6a23c;
}

.label-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.label-info {
  flex: 1;
}

.label-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  word-break: break-all;
}

.label-id {
  font-size: 12px;
  color: #909399;
}

.label-actions {
  flex-shrink: 0;
  margin-left: 8px;
}

.action-btn {
  padding: 4px;
  color: #909399;
}

.action-btn:hover {
  color: #409eff;
}

.delete-item {
  color: #f56c6c;
}

.label-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.stat-value.zero {
  color: #e6a23c;
}

.usage-bar {
  margin-bottom: 16px;
}

.usage-bar-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.usage-bar-text {
  font-size: 12px;
  color: #606266;
  text-align: right;
  margin-top: 4px;
}

.label-footer {
  text-align: center;
}

:deep(.el-progress-bar__outer) {
  border-radius: 3px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 3px;
}
</style> 