<!--
  搜索结果项组件 - 简化高效设计
-->
<template>
  <div
    class="result-item-card"
    :class="{ 
      'selected': isSelected,
      'expandable': item.text.length > 300 
    }"
    @click="emit('toggleSelection')"
  >
    <!-- 卡片序号标识 -->
    <div class="card-index">{{ index }}</div>
    
    <!-- 卡片主要内容 -->
    <div class="card-content">
      <!-- 头部信息行 - 合并统计信息 -->
      <div class="item-header">
        <div class="header-left">
          <el-checkbox
            :model-value="isSelected"
            @change="emit('toggleSelection')"
            @click.stop
            class="item-checkbox"
          />
          <span class="item-id">ID {{ item.id }}</span>
          <!-- 字符统计信息移至头部 -->
          <span class="char-count">
            {{ item.text.length }} chars
          </span>
        </div>
        
        <!-- 标签区域 -->
        <div class="item-labels">
          <template v-if="getLabelsArray(item.labels).length > 0">
            <el-tag
              v-for="label in getLabelsArray(item.labels)"
              :key="label"
              type="primary"
              size="small"
              class="label-tag"
            >
              {{ label }}
            </el-tag>
          </template>
          <el-tag v-else type="info" size="small" class="no-labels-tag">
            <i class="fas fa-tag"></i>
            未标注
          </el-tag>
        </div>
      </div>
      
      <!-- 文本内容区域 -->
      <div 
        class="text-section"
        :class="{ 'expanded': expandedItems.has(item.id) }"
      >
        <div 
          :data-highlight="keywords?.join(',')"
          class="text-content"
          v-html="highlightedDisplayText"
        ></div>
        
        <!-- 展开/收起按钮 -->
        <el-button 
          v-if="item.text.length > 300" 
          @click.stop="toggleExpanded(item.id)"
          type="primary"
          size="small"
          text
          class="expand-button"
          :title="expandedItems.has(item.id) ? '收起' : '展开全文'"
        >
          <i :class="expandedItems.has(item.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
          {{ expandedItems.has(item.id) ? '收起' : '展开' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AnnotationDataResponse } from '@/types/api'
import { parseLabels } from '@/utils/labelUtils'

// Props
interface Props {
  item: AnnotationDataResponse
  index: number
  isSelected: boolean
  keywords?: string[]
}

// Emits
interface Emits {
  'toggleSelection': []
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 展开状态管理
const expandedItems = ref<Set<number>>(new Set())

// 方法
const getLabelsArray = (labels: string | null | undefined): string[] => {
  return parseLabels(labels)
}

const toggleExpanded = (id: number) => {
  if (expandedItems.value.has(id)) {
    expandedItems.value.delete(id)
  } else {
    expandedItems.value.add(id)
  }
}

const getDisplayText = (text: AnnotationDataResponse): string => {
  if (text.text.length <= 300 || expandedItems.value.has(text.id)) {
    return text.text
  }
  return text.text.substring(0, 300) + '...'
}

// 高亮关键词功能
const highlightText = (text: string, keywords: string[]): string => {
  if (!keywords || keywords.length === 0) {
    return text
  }
  
  let highlightedText = text
  keywords.forEach(keyword => {
    if (keyword && keyword.trim()) {
      const regex = new RegExp(`(${keyword.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
      highlightedText = highlightedText.replace(regex, '<mark class="keyword-highlight">$1</mark>')
    }
  })
  
  return highlightedText
}

// 计算高亮后的显示文本
const highlightedDisplayText = computed(() => {
  const displayText = getDisplayText(props.item)
  return highlightText(displayText, props.keywords || [])
})
</script>

<style scoped>
.result-item-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 0;
  margin-bottom: 12px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.result-item-card:hover {
  border-color: var(--el-color-primary);
}

.result-item-card.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.result-item-card.selected::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--el-color-primary);
  z-index: 2;
}

/* 卡片序号标识 */
.card-index {
  position: absolute;
  top: 12px;
  right: 16px;
  background: #f5f7fa;
  color: var(--el-text-color-regular);
  width: 28px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
  z-index: 1;
  border: 1px solid #e4e7ed;
}

.result-item-card.selected .card-index {
  background: var(--el-color-primary);
  color: white;
  border-color: var(--el-color-primary);
}

.card-content {
  padding: 16px;
  padding-right: 48px;
}

/* 头部信息行 */
.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.item-id {
  font-size: 12px;
  color: var(--el-text-color-regular);
  font-weight: 500;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

/* 字符统计信息样式 - 移至头部 */
.char-count {
  font-size: 11px;
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.char-count i {
  font-size: 9px;
  opacity: 0.7;
}

.item-labels {
  display: flex;
  gap: 6px;
  flex: 1;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.label-tag {
  font-weight: 500;
}

.no-labels-tag {
  font-weight: 500;
}

.no-labels-tag i {
  font-size: 10px;
  margin-right: 4px;
}

/* 文本内容区域 */
.text-section {
  position: relative;
}

.text-content {
  font-size: 14px;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  word-break: break-word;
  margin-bottom: 8px;
}

.text-section.expanded .text-content {
  white-space: pre-wrap;
}

.expand-button {
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
  margin-top: 4px;
}

.expand-button i {
  margin-right: 4px;
  font-size: 10px;
}

/* 关键词高亮样式 */
:deep(.keyword-highlight) {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  color: #856404;
  padding: 1px 3px;
  border-radius: 3px;
  font-weight: 600;
  border: 1px solid #ffeaa7;
  box-shadow: 0 1px 2px rgba(133, 100, 4, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-content {
    padding: 12px;
    padding-right: 40px;
  }
  
  .card-index {
    top: 8px;
    right: 12px;
    width: 24px;
    height: 16px;
    font-size: 10px;
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
  
  .header-left {
    flex-wrap: wrap;
  }
  
  .item-labels {
    justify-content: flex-start;
  }
}
</style>

