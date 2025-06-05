<!--
  筛选条件面板组件
-->
<template>
  <div class="filter-panel glass-panel">
    <div class="section-header">
      <h2>
        <i class="fas fa-filter"></i>
        筛选条件
      </h2>
    </div>

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
            size="small"
          />
          <el-button
            type="primary"
            size="small"
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
            size="small"
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
            size="small"
          />
          <el-button
            type="danger"
            size="small"
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
            size="small"
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
        <div class="keyword-input">
          <el-select
            v-model="labelInput.include"
            placeholder="请选择标签"
            size="small"
            filterable
            clearable
            style="flex: 1"
          >
            <el-option
              v-for="option in availableLabelOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <el-button
            type="primary"
            size="small"
            @click="addIncludeLabel"
            :disabled="!labelInput.include"
          >
            添加
          </el-button>
        </div>
        <div class="keyword-tags" v-if="includeLabels.length > 0">
          <el-tag
            v-for="(label, index) in includeLabels"
            :key="`include-label-${index}`"
            closable
            type="success"
            size="small"
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
        <div class="keyword-input">
          <el-select
            v-model="labelInput.exclude"
            placeholder="请选择标签"
            size="small"
            filterable
            clearable
            style="flex: 1"
          >
            <el-option
              v-for="option in availableLabelOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <el-button
            type="danger"
            size="small"
            @click="addExcludeLabel"
            :disabled="!labelInput.exclude"
          >
            添加
          </el-button>
        </div>
        <div class="keyword-tags" v-if="excludeLabels.length > 0">
          <el-tag
            v-for="(label, index) in excludeLabels"
            :key="`exclude-label-${index}`"
            closable
            type="danger"
            size="small"
            @close="removeExcludeLabel(index)"
          >
            {{ label }}
          </el-tag>
        </div>
      </div>

      <!-- 未标注筛选 -->
      <div class="form-group">
        <el-checkbox
          v-model="unlabeledOnly"
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
          :loading="isLoading"
          :disabled="!hasFilterConditions"
          @click="$emit('preview')"
        />
        <ModernButton
          text="执行筛选"
          icon="fas fa-search"
          :loading="isLoading"
          :disabled="!hasFilterConditions"
          @click="$emit('filter')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted } from 'vue'
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
const addIncludeLabel = () => {
  const label = labelInput.include
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

const addExcludeLabel = () => {
  const label = labelInput.exclude
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

// 未标注筛选
const unlabeledOnly = computed({
  get: () => props.unlabeledOnly,
  set: (value: boolean) => emit('update:unlabeledOnly', value)
})

// 生命周期
onMounted(async () => {
  // 初始化标签数据
  if (!labelStore.hasLabels) {
    await labelStore.fetchLabels()
  }
})
</script>

<style scoped>
.filter-panel {
  padding: var(--spacing-xl);
  height: fit-content;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.filter-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
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
  margin-top: var(--spacing-xs);
}

.filter-actions {
  display: flex;
  gap: var(--spacing-md);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--el-border-color-lighter);
}
</style> 