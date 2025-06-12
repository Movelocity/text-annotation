<template>
  <el-card class="label-card" :class="{ 'unused': isUnused }">
    <div class="label-content">
      <div class="label-header">
        <h4 class="label-name">{{ label.label }}</h4>
        <div class="label-actions">
          <el-button 
            type="text" 
            size="small" 
            @click="emit('edit', label)"
            :icon="Edit"
          />
          <el-button 
            type="text" 
            size="small" 
            @click="emit('delete', label)"
            :icon="Delete"
            class="delete-btn"
          />
        </div>
      </div>

      <div v-if="label.description" class="label-description">
        {{ label.description }}
      </div>

      <div class="label-footer">
        <div v-if="label.groups" class="label-group">
          <el-icon><Folder /></el-icon>
          <span>{{ label.groups }}</span>
        </div>
        <div class="label-usage">
          <el-tag :type="isUnused ? 'warning' : 'success'" size="small">
            {{ usageCount }}次使用
          </el-tag>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Delete, Edit, Folder } from '@element-plus/icons-vue'
import type { LabelResponse, LabelStats } from '@/types/api'

interface Props {
  label: LabelResponse
  stats: LabelStats | null
  maxUsageCount?: number
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
</script>

<style scoped>
.label-card {
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 1px solid #e4e7ed;
}

.label-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.label-card.unused {
  border-left: 3px solid #f39c12;
}

.label-content {
  padding: 4px;
}

.label-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.label-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0;
  flex: 1;
  margin-right: 8px;
  word-break: break-word;
}

.label-actions {
  display: flex;
  gap: 4px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.label-card:hover .label-actions {
  opacity: 1;
}

.delete-btn {
  color: #f56c6c;
}

.label-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.4;
}

.label-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.label-group {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  flex: 1;
}

.label-group span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.label-usage {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .label-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style> 