<!--
  筛选条件Tab组件
  功能：关键词筛选、标签筛选、未标注筛选等
-->
<template>
  <div class="filter-conditions-tab">
    <div class="filter-form">
      <!-- 关键词筛选 -->
      <div class="form-group">
        <label class="form-label">
          <i class="fas fa-search"></i>
          包含关键词
        </label>
        <div class="keyword-input">
          <el-input
            v-model="keywordInput.include"
            placeholder="输入关键词，按回车添加"
            @keydown.enter="addIncludeKeyword"
            size="default"
          />
          <el-button
            type="primary"
            size="default"
            @click="addIncludeKeyword"
            :disabled="!keywordInput.include.trim()"
          >
            添加
          </el-button>
        </div>
        <div class="keyword-tags" v-if="includeKeywords.length > 0">
          <el-tag
            v-for="(keyword, index) in includeKeywords"
            :key="`include-${index}`"
            closable
            type="success"
            size="default"
            style="font-size: 14px; font-weight: bold;"
            @close="removeIncludeKeyword(index)"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">
          <i class="fas fa-times"></i>
          不包含关键词
        </label>
        <div class="keyword-input">
          <el-input
            v-model="keywordInput.exclude"
            placeholder="输入关键词，按回车添加"
            @keydown.enter="addExcludeKeyword"
            size="default"
          />
          <el-button
            type="danger"
            size="default"
            @click="addExcludeKeyword"
            :disabled="!keywordInput.exclude.trim()"
          >
            添加
          </el-button>
        </div>
        <div class="keyword-tags" v-if="excludeKeywords.length > 0">
          <el-tag
            v-for="(keyword, index) in excludeKeywords"
            :key="`exclude-${index}`"
            closable
            type="danger"
            size="medium"
            style="font-size: 14px; font-weight: bold;"
            @close="removeExcludeKeyword(index)"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </div>

      <!-- 标签筛选 -->
      <div class="form-group">
        <label class="form-label">
          <i class="fas fa-tag"></i>
          包含标签
        </label>
        <el-select
          v-model="labelInput.include"
          placeholder="请选择标签，选择后自动添加"
          size="default"
          filterable
          clearable
          @change="addIncludeLabel"
        >
          <el-option
            v-for="option in availableLabelOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <div class="keyword-tags" v-if="includeLabels.length > 0">
          <el-tag
            v-for="(label, index) in includeLabels"
            :key="`include-label-${index}`"
            closable
            type="success"
            size="default"
            style="font-size: 14px; font-weight: bold;"
            @close="removeIncludeLabel(index)"
          >
            {{ label }}
          </el-tag>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">
          <i class="fas fa-ban"></i>
          不包含标签
        </label>
        <el-select
          v-model="labelInput.exclude"
          placeholder="请选择标签，选择后自动添加"
          size="default"
          filterable
          clearable
          @change="addExcludeLabel"
        >
          <el-option
            v-for="option in availableLabelOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <div class="keyword-tags" v-if="excludeLabels.length > 0">
          <el-tag
            v-for="(label, index) in excludeLabels"
            :key="`exclude-label-${index}`"
            closable
            type="danger"
            size="medium"
            @close="removeExcludeLabel(index)"
            style="font-size: 14px; font-weight: bold;"
          >
            {{ label }}
          </el-tag>
        </div>
      </div>

      <!-- 未标注筛选 -->
      <div class="form-group">
        <el-checkbox
          v-model="unlabeledOnlyModel"
          size="large"
        >
          <i class="fas fa-question-circle"></i>
          仅显示未标注的文本
        </el-checkbox>
      </div>

      <!-- 操作按钮 -->
      <div class="filter-actions">
        <ModernButton
          text="预览筛选"
          icon="fas fa-eye"
          size="large"
          :loading="isLoading"
          :disabled="!hasFilterConditions"
          @click="$emit('preview')"
        />
        <ModernButton
          text="执行筛选"
          icon="fas fa-search"
          size="large"
          variant="primary"
          :loading="isLoading"
          :disabled="!hasFilterConditions"
          @click="handleFilter"
        />
      </div>
      
      <!-- 快捷键提示 -->
      <div class="shortcut-hint">
        <i class="fas fa-keyboard"></i>
        <span>快捷键：Ctrl + Enter 执行筛选</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted, onUnmounted, ref } from 'vue'
import { useLabelStore } from '@/stores/label'
import ModernButton from '../common/ModernButton.vue'

// Props
interface Props {
  includeKeywords: string[]
  excludeKeywords: string[]
  includeLabels: string[]
  excludeLabels: string[]
  unlabeledOnly: boolean
  isLoading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  includeKeywords: () => [],
  excludeKeywords: () => [],
  includeLabels: () => [],
  excludeLabels: () => [],
  unlabeledOnly: false,
  isLoading: false
})

// Emits
interface Emits {
  'update:includeKeywords': [keywords: string[]]
  'update:excludeKeywords': [keywords: string[]]
  'update:includeLabels': [labels: string[]]
  'update:excludeLabels': [labels: string[]]
  'update:unlabeledOnly': [unlabeledOnly: boolean]
  'preview': []
  'filter': []
}

const emit = defineEmits<Emits>()

// Store
const labelStore = useLabelStore()

// 防抖定时器
const debounceTimer = ref<number | null>(null)

// 表单数据
const keywordInput = reactive({
  include: '',
  exclude: ''
})

const labelInput = reactive({
  include: '',
  exclude: ''
})

// 计算属性
const hasFilterConditions = computed(() => {
  return !!(
    props.includeKeywords.length ||
    props.excludeKeywords.length ||
    props.includeLabels.length ||
    props.excludeLabels.length ||
    props.unlabeledOnly
  )
})

// 可用标签选项
const availableLabelOptions = computed(() => {
  return labelStore.labelOptions.filter(option => 
    !props.includeLabels.includes(option.value) && 
    !props.excludeLabels.includes(option.value)
  )
})

// 未标注筛选的双向绑定
const unlabeledOnlyModel = computed({
  get: () => props.unlabeledOnly,
  set: (value: boolean) => emit('update:unlabeledOnly', value)
})

// 带防抖的筛选执行函数
const handleFilter = () => {
  if (!hasFilterConditions.value || props.isLoading) {
    console.log('no filter conditions')
    return
  }
  
  // 清除之前的定时器
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
  }
  
  // 设置新的防抖定时器
  debounceTimer.value = setTimeout(() => {
    console.log('emit filter')
    emit('filter')
    debounceTimer.value = null
  }, 800) // 0.8秒防抖
}

// 键盘事件处理函数
const handleKeydown = (event: KeyboardEvent) => {
  // 检查是否在输入框或可编辑元素中
  const target = event.target as HTMLElement
  const isInputElement = target && (
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.isContentEditable ||
    target.closest('.el-input__wrapper') ||
    target.closest('.el-select') ||
    target.closest('.el-textarea')
  )

  // 检查是否为 Ctrl + Enter 组合键
  if (event.ctrlKey && event.key === 'Enter') {
    // 如果在输入框中，允许默认行为（换行等）
    if (!isInputElement) {
      event.preventDefault()
      handleFilter()
    }
  }
}

// 关键词管理
const addIncludeKeyword = () => {
  const keyword = keywordInput.include.trim()
  if (keyword && !props.includeKeywords.includes(keyword)) {
    emit('update:includeKeywords', [...props.includeKeywords, keyword])
    keywordInput.include = ''
  }
}

const removeIncludeKeyword = (index: number) => {
  const current = [...props.includeKeywords]
  current.splice(index, 1)
  emit('update:includeKeywords', current)
}

const addExcludeKeyword = () => {
  const keyword = keywordInput.exclude.trim()
  if (keyword && !props.excludeKeywords.includes(keyword)) {
    emit('update:excludeKeywords', [...props.excludeKeywords, keyword])
    keywordInput.exclude = ''
  }
}

const removeExcludeKeyword = (index: number) => {
  const current = [...props.excludeKeywords]
  current.splice(index, 1)
  emit('update:excludeKeywords', current)
}

// 标签管理
const addIncludeLabel = (value?: string) => {
  const label = value || labelInput.include
  if (label && !props.includeLabels.includes(label)) {
    emit('update:includeLabels', [...props.includeLabels, label])
    labelInput.include = ''
  }
}

const removeIncludeLabel = (index: number) => {
  const current = [...props.includeLabels]
  current.splice(index, 1)
  emit('update:includeLabels', current)
}

const addExcludeLabel = (value?: string) => {
  const label = value || labelInput.exclude
  if (label && !props.excludeLabels.includes(label)) {
    emit('update:excludeLabels', [...props.excludeLabels, label])
    labelInput.exclude = ''
  }
}

const removeExcludeLabel = (index: number) => {
  const current = [...props.excludeLabels]
  current.splice(index, 1)
  emit('update:excludeLabels', current)
}

// 生命周期
onMounted(async () => {
  // 添加全局键盘事件监听
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  // 清理定时器
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
  }
  
  // 移除全局键盘事件监听
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.filter-conditions-tab {
  height: 100%;
  padding: 8px 12px;
}

.filter-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  height: 100%;
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

.keyword-input {
  display: flex;
  gap: var(--spacing-sm);
}

.keyword-input .el-input {
  flex: 1;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.filter-actions {
  display: flex;
  justify-content: space-around;
  gap: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
}

.shortcut-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xs);
  font-size: 11px;
  color: var(--el-text-color-secondary);
  border-radius: var(--el-border-radius-base);
}

.shortcut-hint i {
  font-size: 14px;
  margin-right: var(--spacing-sm);
}
</style> 