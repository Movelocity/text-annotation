<!--
  文本列表组件
  功能：显示文本列表，支持分页、筛选、选择
-->
<template>
  <div class="text-list">
    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :model="filterForm" inline class="filter-form">
        <el-form-item label="状态筛选">
          <el-select v-model="filterForm.unlabeled_only" placeholder="选择状态" @change="handleFilterChange">
            <el-option label="全部" :value="false" />
            <el-option label="未标注" :value="true" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容搜索">
          <el-input
            v-model="filterForm.query"
            placeholder="搜索文本内容"
            clearable
            @input="handleQueryInput"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 列表区域 -->
    <div class="list-container" v-loading="loading">
      <div v-if="!hasAnnotations && !loading" class="empty-state">
        <el-empty description="暂无数据" />
      </div>
      
      <div v-else class="text-items">
        <div
          v-for="(item, index) in annotations"
          :key="item.id"
          class="text-item"
          :class="{ 
            'selected': selectedItem?.id === item.id,
            'labeled': item.labels,
            'unlabeled': !item.labels
          }"
          @click="handleItemClick(item, index)"
        >
          <div class="item-header">
            <div class="item-id">#{{ item.id }}</div>
            <div class="item-status">
              <el-tag
                v-if="item.labels"
                type="success"
                size="small"
              >
                {{ item.labels }}
              </el-tag>
              <el-tag
                v-else
                type="info"
                size="small"
              >
                未标注
              </el-tag>
            </div>
          </div>
          <div class="item-content">
            {{ truncateText(item.text, 100) }}
          </div>
          <div class="item-meta">
            <span class="item-length">{{ item.text.length }} 字符</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页区域 -->
    <div class="pagination-section" v-if="hasAnnotations">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="total"
        :disabled="loading"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useAnnotationStore } from '../../stores/annotation'
import type { AnnotationDataResponse } from '../../types/api'

// Props
interface Props {
  selectedItem?: AnnotationDataResponse | null
}

// Emits
interface Emits {
  (e: 'item-select', item: AnnotationDataResponse, index: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Store
const annotationStore = useAnnotationStore()

// 响应式数据
const filterForm = ref({
  unlabeled_only: false,
  query: ''
})

const searchTimeout = ref<number | null>(null)

// 计算属性
const annotations = computed(() => annotationStore.annotations)
const loading = computed(() => annotationStore.loading)
const total = computed(() => annotationStore.total)
const hasAnnotations = computed(() => annotationStore.hasAnnotations)
const currentPage = computed(() => annotationStore.searchParams.page || 1)
const pageSize = computed(() => annotationStore.searchParams.per_page || 50)

// 方法
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatTime = (timeStr: string): string => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const handleItemClick = (item: AnnotationDataResponse, index: number) => {
  emit('item-select', item, index)
}

const handleFilterChange = () => {
  handleSearch()
}

const handleQueryInput = () => {
  // 防抖搜索
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    handleSearch()
  }, 500)
}

const handleSearch = async () => {
  try {
    await annotationStore.searchAnnotations({
      page: 1,
      per_page: pageSize.value,
      unlabeled_only: filterForm.value.unlabeled_only,
      query: filterForm.value.query || undefined
    })
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

const handleReset = () => {
  filterForm.value = {
    unlabeled_only: false,
    query: ''
  }
  annotationStore.resetSearch()
  loadData()
}

const handleSizeChange = async (size: number) => {
  try {
    await annotationStore.searchAnnotations({
      page: 1,
      per_page: size
    })
  } catch (error) {
    console.error('更改页面大小失败:', error)
  }
}

const handleCurrentChange = async (page: number) => {
  try {
    await annotationStore.searchAnnotations({
      page
    })
  } catch (error) {
    console.error('切换页面失败:', error)
  }
}

const loadData = async () => {
  try {
    await annotationStore.searchAnnotations()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadData()
})

// 监听器
watch(() => props.selectedItem, (newItem) => {
  // 当外部选择的项目改变时，可以添加额外的逻辑
}, { deep: true })
</script>

<style scoped>
.text-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-section {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
}

.filter-form {
  margin: 0;
}

.list-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.empty-state {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.text-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--el-bg-color);
}

.text-item:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.text-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.text-item.labeled {
  border-left: 4px solid var(--el-color-success);
}

.text-item.unlabeled {
  border-left: 4px solid var(--el-color-info);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-id {
  font-weight: 600;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.item-content {
  color: var(--el-text-color-primary);
  line-height: 1.5;
  margin-bottom: 8px;
  word-break: break-word;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.pagination-section {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
  background: var(--el-bg-color);
}
</style> 