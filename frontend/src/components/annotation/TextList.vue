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
        
        <div class="filter-options">
          <div class="status-filter">
            <el-radio-group v-model="filterForm.unlabeled_only" @change="handleFilterChange" class="status-radio">
              <el-radio-button :label="false">
                <i class="fas fa-list-ul"></i>
                全部
              </el-radio-button>
              <el-radio-button :label="true">
                <i class="fas fa-clock"></i>
                未标注
              </el-radio-button>
            </el-radio-group>
          </div>
          
          <el-button @click="handleReset" class="reset-btn" size="small">
            <i class="fas fa-undo"></i>
            重置
          </el-button>
        </div>
      </div>
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
          class="text-item modern-card transform-hover"
          :class="{ 
            'selected': selectedItem?.id === item.id,
            'labeled': item.labels,
            'unlabeled': !item.labels
          }"
          @click="handleItemClick(item, index)"
        >
          <div class="item-indicator">
            <div class="status-dot" :class="{ 'completed': item.labels, 'pending': !item.labels }"></div>
          </div>
          
          <div class="item-main">
            <div class="item-header">
              <div class="item-id">
                <i class="fas fa-hashtag"></i>
                {{ item.id }}
              </div>
              <div class="item-status">
                <div v-if="item.labels" class="status-badge success">
                  <i class="fas fa-check-circle"></i>
                  {{ item.labels }}
                </div>
                <div v-else class="status-badge pending">
                  <i class="fas fa-clock"></i>
                  待标注
                </div>
              </div>
            </div>
            
            <div class="item-content">
              <p class="content-preview">{{ truncateText(item.text, 120) }}</p>
            </div>
            
            <div class="item-meta">
              <div class="meta-item">
                <i class="fas fa-font"></i>
                <span>{{ item.text.length }} 字符</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-layer-group"></i>
                <span>{{ item.text.split('\n').length }} 行</span>
              </div>
            </div>
          </div>
          
          <div class="item-actions">
            <div class="select-indicator">
              <i class="fas fa-chevron-right"></i>
            </div>
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
// import { Search } from '@element-plus/icons-vue'
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
watch(() => props.selectedItem, () => {
  // 当外部选择的项目改变时，可以添加额外的逻辑
}, { deep: true })
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

.search-wrapper {
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
  border: 2px solid var(--el-border-color-light);
  transition: all var(--duration-fast) ease;
}

.search-input :deep(.el-input__wrapper):hover {
  border-color: var(--el-color-primary-light-5);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
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

.status-radio {
  width: 100%;
}

.status-radio :deep(.el-radio-button) {
  flex: 1;
}

.status-radio :deep(.el-radio-button__inner) {
  width: 100%;
  border-radius: var(--radius-md);
  border: 2px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  transition: all var(--duration-fast) ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.status-radio :deep(.el-radio-button__inner):hover {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.status-radio :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.reset-btn {
  border-radius: var(--radius-md);
  border: 2px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  transition: all var(--duration-fast) ease;
}

.reset-btn:hover {
  border-color: var(--el-color-warning);
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning-dark-2);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.reset-btn i {
  margin-right: 4px;
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

/* 文本项 */
.text-item {
  display: flex;
  align-items: stretch;
  background: var(--el-bg-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--duration-normal) ease;
  overflow: hidden;
  position: relative;
}

.text-item:hover {
  border-color: var(--el-color-primary-light-7);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.text-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.text-item.selected::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
}

.item-indicator {
  display: flex;
  align-items: center;
  padding: 0 12px;
  background: var(--el-bg-color-page);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
  transition: all var(--duration-fast) ease;
}

.status-dot.completed {
  background: var(--el-color-success);
  box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.2);
}

.status-dot.pending {
  background: var(--el-color-warning);
  box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.2);
}

.status-dot.completed::before {
  content: '\f00c';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 8px;
}

.item-main {
  flex: 1;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-id {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.item-id i {
  font-size: 0.75rem;
  color: var(--el-color-primary);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.success {
  background: var(--el-color-success-light-9);
  color: var(--el-color-success-dark-2);
  border: 1px solid var(--el-color-success-light-5);
}

.status-badge.pending {
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning-dark-2);
  border: 1px solid var(--el-color-warning-light-5);
}

.item-content {
  flex: 1;
}

.content-preview {
  margin: 0;
  color: var(--el-text-color-primary);
  line-height: 1.6;
  font-size: 0.875rem;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.meta-item i {
  font-size: 0.675rem;
  opacity: 0.8;
}

.item-actions {
  display: flex;
  align-items: center;
  padding: 0 16px;
  background: var(--el-bg-color-page);
}

.select-indicator {
  color: var(--el-text-color-placeholder);
  font-size: 16px;
  transition: all var(--duration-fast) ease;
}

.text-item:hover .select-indicator {
  color: var(--el-color-primary);
  transform: translateX(4px);
}

.text-item.selected .select-indicator {
  color: var(--el-color-primary);
  transform: translateX(4px);
}

/* 分页区域 */
.pagination-section {
  padding: 20px;
  border-top: 2px solid var(--el-border-color-lighter);
  flex-shrink: 0;
  background: var(--el-bg-color);
  display: flex;
  justify-content: center;
}

.pagination-section :deep(.el-pagination) {
  --el-pagination-button-color: var(--el-text-color-regular);
  --el-pagination-hover-color: var(--el-color-primary);
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
  
  .text-item {
    flex-direction: column;
  }
  
  .item-indicator {
    padding: 8px 12px;
  }
  
  .item-main {
    padding: 12px 16px;
  }
  
  .item-actions {
    padding: 8px 16px;
    justify-content: center;
  }
  
  .pagination-section {
    padding: 16px;
  }
}
</style> 