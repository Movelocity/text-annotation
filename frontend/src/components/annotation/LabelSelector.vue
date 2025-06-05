<!--
  标签选择器组件
  功能：显示标签列表，选择标签，保存标注
-->
<template>
  <div class="label-selector">
    <div class="selector-header">
      <h3>标签选择</h3>
      <div class="quick-actions">
        <ModernButton
          text="保存标注"
          icon="fas fa-save"
          :disabled="!currentItem || saving"
          :loading="saving"
          @click="handleSave"
        />
        <ModernButton
          text="跳过"
          icon="fas fa-step-forward"
          :disabled="!currentItem"
          @click="handleSkip"
        />
      </div>
    </div>

    <div v-if="!currentItem" class="no-selection">
      <el-empty description="请选择要标注的文本" />
    </div>

    <div v-else class="selector-content">
      <!-- 当前标签显示 -->
      <div class="current-label-section">
        <div class="section-title">
          当前标签
          <el-button
            v-if="selectedLabels.length > 0"
            type="danger"
            size="small"
            text
            @click="handleClearAllLabels"
            class="clear-all-btn"
          >
            清除所有
          </el-button>
        </div>
        <div class="current-label">
          <template v-if="selectedLabels.length > 0">
            <el-tag
              v-for="label in selectedLabels"
              :key="label"
              type="success"
              size="large"
              style="font-size: 14px; font-weight: bold;"
              closable
              @close="handleRemoveLabel(label)"
              class="label-tag"
            >
              {{ label }}
            </el-tag>
          </template>
          <span v-else class="no-label">未标注</span>
        </div>
      </div>

      <!-- 标签选择区域 -->
      <div class="label-selection-section">
        <div class="section-title">选择标签</div>
        
        <!-- 搜索框 -->
        <div class="search-section">
          <el-input
            v-model="labelSearch"
            placeholder="搜索标签..."
            clearable
            prefix-icon="Search"
          />
        </div>

        <!-- 标签列表 -->
        <div class="labels-container" v-loading="labelsLoading">
          <div v-if="!hasLabels && !labelsLoading" class="empty-labels">
            <el-empty description="暂无标签" />
          </div>
          
          <div v-else class="labels-grid">
            <div
              v-for="(label, index) in filteredLabels"
              :key="label.id"
              class="label-item"
              :class="{ 
                'selected': selectedLabels.includes(label.label),
                'shortcut': index < 9
              }"
              @click="handleLabelToggle(label.label)"
            >
              <div class="label-content">
                <span class="label-text">{{ label.label }}</span>
                <span v-if="index < 9" class="shortcut-key">{{ index + 1 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作提示 -->
      <div class="shortcuts-hint">
        <div class="hint-title">快捷键提示</div>
        <div class="hint-content">
          <span>数字键 1-9：切换对应标签</span>
          <span>Enter：保存标注</span>
          <span>Space：跳过</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useLabelStore } from '@/stores/label'
import { useAnnotationStore } from '@/stores/annotation'
import type { AnnotationDataResponse } from '@/types/api'
import { ElMessage } from 'element-plus'
import ModernButton from '@/components/common/ModernButton.vue'

// Props
interface Props {
  currentItem?: AnnotationDataResponse | null
}

// Emits
interface Emits {
  (e: 'save-success'): void
  (e: 'skip'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Stores
const labelStore = useLabelStore()
const annotationStore = useAnnotationStore()

// 响应式数据
const selectedLabels = ref<string[]>([])
const labelSearch = ref('')
const saving = ref(false)

// 计算属性
const labels = computed(() => labelStore.labels)
const labelsLoading = computed(() => labelStore.loading)
const hasLabels = computed(() => labelStore.hasLabels)

const filteredLabels = computed(() => {
  if (!labelSearch.value) return labels.value
  return labels.value.filter(label => 
    label.label.toLowerCase().includes(labelSearch.value.toLowerCase())
  )
})

// 方法
const handleLabelToggle = (labelText: string) => {
  const index = selectedLabels.value.indexOf(labelText)
  if (index > -1) {
    selectedLabels.value.splice(index, 1)
  } else {
    selectedLabels.value.push(labelText)
  }
}

const handleRemoveLabel = (labelText: string) => {
  const index = selectedLabels.value.indexOf(labelText)
  if (index > -1) {
    selectedLabels.value.splice(index, 1)
  }
}

const handleClearAllLabels = () => {
  selectedLabels.value = []
}

const handleSave = async () => {
  if (!props.currentItem) return

  try {
    saving.value = true
    await annotationStore.updateAnnotation(props.currentItem.id, {
      labels: selectedLabels.value.length > 0 ? selectedLabels.value.join(', ') : null
    })
    ElMessage.success('标注保存成功')
    emit('save-success')
  } catch (error) {
    console.error('保存标注失败:', error)
    ElMessage.error('保存标注失败')
  } finally {
    saving.value = false
  }
}

const handleSkip = () => {
  selectedLabels.value = []
  emit('skip')
}

const loadLabels = async () => {
  try {
    await labelStore.fetchLabels()
  } catch (error) {
    console.error('加载标签失败:', error)
    ElMessage.error('加载标签失败')
  }
}

// 快捷键处理
const handleKeyDown = (event: KeyboardEvent) => {
  if (!props.currentItem) return

  // 数字键 1-9 切换标签
  if (event.key >= '1' && event.key <= '9') {
    const index = parseInt(event.key) - 1
    if (index < filteredLabels.value.length) {
      handleLabelToggle(filteredLabels.value[index].label)
      event.preventDefault()
    }
  }
  
  // Enter 保存
  if (event.key === 'Enter') {
    handleSave()
    event.preventDefault()
  }
  
  // Space 跳过
  if (event.key === ' ' || event.key === 'Space') {
    handleSkip()
    event.preventDefault()
  }
}

// 监听器
watch(() => props.currentItem, (newItem) => {
  if (newItem && newItem.labels) {
    // 解析逗号分隔的标签字符串为数组
    selectedLabels.value = newItem.labels.split(',').map(label => label.trim()).filter(label => label)
  } else {
    selectedLabels.value = []
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  loadLabels()
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.label-selector {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.selector-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.no-selection {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.selector-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clear-all-btn {
  font-size: 12px;
}

.current-label-section {
  flex-shrink: 0;
}

.current-label {
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
  min-height: 44px;
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
}

.no-label {
  color: var(--el-text-color-secondary);
  font-style: italic;
}

.label-selection-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.search-section {
  margin-bottom: 12px;
}

.labels-container {
  flex: 1;
  min-height: 200px;
}

.empty-labels {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.labels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  max-height: 360px;
  overflow-y: auto;
}

.label-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-primary);
  position: relative;
}

.label-item:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.label-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.label-item.shortcut {
  border-left: 3px solid var(--el-color-warning);
}

.label-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label-text {
  font-weight: 500;
  word-break: break-word;
}

.shortcut-key {
  background: var(--el-color-warning);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 12px;
  font-weight: bold;
  flex-shrink: 0;
  margin-left: 8px;
}

.shortcuts-hint {
  flex-shrink: 0;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
}

.hint-title {
  font-weight: 600;
  font-size: 12px;
  color: var(--el-text-color-primary);
  margin-bottom: 6px;
}

.hint-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: var(--el-text-color-secondary);
}
</style> 