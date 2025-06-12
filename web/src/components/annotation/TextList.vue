<!--
  文本列表组件
  功能：显示文本列表，支持分页、筛选、选择
-->
<template>
  <div class="text-list">
    <!-- 筛选区域 -->
    <div class="filter-section">
      <div class="filter-header">
        <div class="section-title">
          <i class="fas fa-list"></i>
          文本列表
        </div>
        <div class="filter-stats">
          <span class="total-badge">{{ total }} 条</span>
        </div>
      </div>
      
      <div class="filter-controls">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <el-input
            v-model="filterForm.query"
            placeholder="搜索文本内容..."
            clearable
            @input="handleQueryInput"
            class="search-input"
          />
        </div>
        
        <div class="label-search-wrapper">
          <i class="fas fa-tags search-icon"></i>
          <el-input
            v-model="filterForm.labels"
            placeholder="搜索标签/分类 (多个用逗号分隔)..."
            clearable
            @input="handleLabelInput"
            class="search-input"
          />
        </div>
        
        <div class="filter-options">
          <div class="status-filter">
            <div class="status-buttons">
              <ModernButton
                text="全部"
                icon="fas fa-list-ul"
                :class="{ active: !filterForm.unlabeled_only }"
                @click="() => { filterForm.unlabeled_only = false; handleFilterChange(); }"
              />
              <ModernButton
                text="未标注"
                icon="fas fa-clock"
                :class="{ active: filterForm.unlabeled_only }"
                @click="() => { filterForm.unlabeled_only = true; handleFilterChange(); }"
              />
            </div>
          </div>
          
          <ModernButton
            text="重置"
            icon="fas fa-undo"
            @click="handleReset"
          />
        </div>
      </div>
    </div>

    <!-- 列表区域 -->
    <div class="list-container" v-loading="loading">
      <div v-if="!hasAnnotations && !loading" class="empty-state">
        <el-empty description="暂无数据" />
      </div>
      
      <div v-else class="text-items">
        <TextItem
          v-for="(item, index) in annotations"
          :key="item.id"
          :item="item"
          :index="index"
          :is-selected="selectedItem?.id === item.id"
          @click="handleItemClick"
        />
      </div>
    </div>

    <!-- 分页区域 -->
    <div class="pagination-section" v-if="hasAnnotations">
      <Pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="total"
        :disabled="loading"
        @page-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
// import { Search } from '@element-plus/icons-vue'
import { useAnnotationStore } from '@/stores/annotation'
import type { AnnotationDataResponse } from '@/types/api'
import TextItem from '@/components/annotation/TextItem.vue'
import Pagination from '@/components/common/Pagination.vue'
import ModernButton from '@/components/common/ModernButton.vue'

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
  query: '',
  labels: ''
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
// const formatTime = (timeStr: string): string => {
//   const date = new Date(timeStr)
//   return date.toLocaleString('zh-CN')
// }

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

const handleLabelInput = () => {
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
      query: filterForm.value.query || undefined,
      labels: filterForm.value.labels || undefined
    })
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

const handleReset = () => {
  filterForm.value = {
    unlabeled_only: false,
    query: '',
    labels: ''
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
watch(() => props.selectedItem, () => {
  // 当外部选择的项目改变时，可以添加额外的逻辑
}, { deep: true })

// 监听store的searchParams变化，同步到本地filterForm
watch(() => annotationStore.searchParams, (newParams) => {
  if (newParams) {
    // 只有在值真正不同时才更新，避免无限循环
    if (filterForm.value.query !== (newParams.query || '')) {
      filterForm.value.query = newParams.query || ''
    }
    if (filterForm.value.labels !== (newParams.labels || '')) {
      filterForm.value.labels = newParams.labels || ''
    }
    if (filterForm.value.unlabeled_only !== (newParams.unlabeled_only || false)) {
      filterForm.value.unlabeled_only = newParams.unlabeled_only || false
    }
  }
}, { deep: true, immediate: true })
</script>

<style scoped>
.text-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color);
}

/* 筛选区域 */
.filter-section {
  padding: 20px;
  border-bottom: 2px solid var(--el-border-color-lighter);
  flex-shrink: 0;
  background: var(--el-bg-color);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.section-title i {
  color: var(--el-color-primary);
  font-size: 1rem;
}

.filter-stats {
  display: flex;
  align-items: center;
  gap: 8px;
}

.total-badge {
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
  color: white;
  padding: 4px 12px;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  box-shadow: var(--shadow-sm);
}

.filter-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-wrapper,
.label-search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--el-text-color-secondary);
  font-size: 14px;
  z-index: 1;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  padding-left: 40px;
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) ease;
}


.filter-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.status-filter {
  flex: 1;
}

.status-buttons {
  display: flex;
  gap: 8px;
  width: 100%;
}

.status-buttons :deep(.modern-btn) {
  flex: 1;
}

.status-buttons :deep(.modern-btn.active) {
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.status-buttons :deep(.modern-btn.active:hover) {
  transform: none;
  background: var(--el-color-primary-dark-2);
}

/* 列表区域 */
.list-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: var(--el-bg-color-page);
}

.empty-state {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}



/* 分页区域 */
.pagination-section {
  padding: 5px;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
  background: var(--el-bg-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-section {
    padding: 16px;
  }
  
  .filter-options {
    flex-direction: column;
    align-items: stretch;
  }
  
  .list-container {
    padding: 12px;
  }
  
  .pagination-section {
    padding: 16px;
  }
}
</style> 