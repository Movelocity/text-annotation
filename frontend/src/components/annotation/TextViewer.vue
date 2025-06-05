<!--
  文本查看器组件
  功能：显示当前选中的文本内容和基本信息
-->
<template>
  <div class="text-viewer">
    <div class="viewer-header">
      <h3>文本内容</h3>
      <div class="text-info" v-if="currentItem">
        <el-tag size="small" type="info">ID: {{ currentItem.id }}</el-tag>
        <el-tag size="small">{{ currentItem.text.length }} 字符</el-tag>
      </div>
    </div>

    <div v-if="!currentItem" class="no-selection">
      <el-empty description="请从左侧列表选择要标注的文本" />
    </div>

    <div v-else class="viewer-content">
      <!-- 文本内容 -->
      <div class="text-content">
        <div class="text-display">
          {{ currentItem.text }}
        </div>
      </div>

      <!-- 当前标签状态 -->
      <div class="label-status">
        <div class="status-title">当前标签</div>
        <div class="status-content">
          <template v-if="currentLabels.length > 0">
            <el-tag
              v-for="label in currentLabels"
              :key="label"
              type="success"
              size="large"
              class="label-tag"
            >
              {{ label }}
            </el-tag>
          </template>
          <span v-else class="no-label">未标注</span>
        </div>
      </div>

      <!-- 文本统计信息 -->
      <div class="text-stats">
        <div class="stats-title">文本统计</div>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">字符数：</span>
            <span class="stat-value">{{ currentItem.text.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">行数：</span>
            <span class="stat-value">{{ lineCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">单词数：</span>
            <span class="stat-value">{{ wordCount }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AnnotationDataResponse } from '../../types/api'

// Props
interface Props {
  currentItem?: AnnotationDataResponse | null
}

const props = defineProps<Props>()

// 计算属性
const currentLabels = computed(() => {
  if (!props.currentItem?.labels) return []
  return props.currentItem.labels.split(',').map(label => label.trim()).filter(label => label)
})

const lineCount = computed(() => {
  if (!props.currentItem) return 0
  return props.currentItem.text.split('\n').length
})

const wordCount = computed(() => {
  if (!props.currentItem) return 0
  // 简单的单词计数，支持中英文
  const text = props.currentItem.text.trim()
  if (!text) return 0
  
  // 中文字符数 + 英文单词数
  const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length
  const englishWords = text.match(/[a-zA-Z]+/g)?.length || 0
  
  return chineseChars + englishWords
})
</script>

<style scoped>
.text-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.viewer-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.text-info {
  display: flex;
  gap: 8px;
}

.no-selection {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.text-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.text-display {
  flex: 1;
  padding: 16px;
  background: var(--el-bg-color-page);
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
  word-break: break-word;
  overflow-y: auto;
  min-height: 200px;
  max-height: 400px;
}

.label-status {
  flex-shrink: 0;
}

.status-title,
.stats-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  font-size: 14px;
}

.status-content {
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
}

.label-tag {
  margin: 2px 0;
}

.no-label {
  color: var(--el-text-color-secondary);
  font-style: italic;
}

.text-stats {
  flex-shrink: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.stat-item {
  padding: 8px 12px;
  background: var(--el-bg-color-page);
  border-radius: 4px;
  border: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-weight: 600;
  color: var(--el-text-color-primary);
  font-size: 14px;
}
</style> 