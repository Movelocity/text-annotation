<!--
  简洁分页组件（紧凑版）
  功能：支持页码导航、每页数量设置、跳转到指定页码
  适配窄宽度容器（500px以内）
-->
<template>
  <div class="pagination" v-if="total > 0">
    <!-- 统计信息 -->
    <div class="pagination-top">
      每页
      <select 
        v-model="currentPageSize" 
        @change="handlePageSizeChange"
        class="page-size-select"
        :disabled="disabled"
      >
        <option v-for="size in pageSizes" :key="size" :value="size">
          {{ size }}条
        </option>
      </select>
    </div>
    
    <!-- 底部：导航控制 -->
    <div class="pagination-controls">
      <button 
        class="pagination-btn"
        :class="{ disabled: currentPage <= 1 }"
        :disabled="disabled || currentPage <= 1"
        @click="handlePrevious"
        title="上一页"
      >
        <i class="fas fa-chevron-left"></i>
      </button>
      
      <div class="page-info">
        <input 
          v-model.number="inputPage"
          @keyup.enter="handleJumpPage"
          @blur="handleJumpPage"
          type="number"
          :min="1"
          :max="totalPages"
          class="page-input"
          :disabled="disabled"
          :placeholder="currentPage.toString()"
        />
        <span class="page-separator">/</span>
        <span class="total-pages">{{ totalPages }}</span>
      </div>
      
      <button 
        class="pagination-btn"
        :class="{ disabled: currentPage >= totalPages }"
        :disabled="disabled || currentPage >= totalPages"
        @click="handleNext"
        title="下一页"
      >
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// Props
interface Props {
  currentPage: number
  pageSize: number
  total: number
  pageSizes?: number[]
  disabled?: boolean
}

// Emits
interface Emits {
  (e: 'page-change', page: number): void
  (e: 'size-change', size: number): void
}

const props = withDefaults(defineProps<Props>(), {
  pageSizes: () => [20, 50, 100, 200],
  disabled: false
})

const emit = defineEmits<Emits>()

// 响应式数据
const currentPageSize = ref(props.pageSize)
const inputPage = ref(props.currentPage)

// 计算属性
const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

// 方法
const handlePrevious = () => {
  if (props.currentPage > 1) {
    emit('page-change', props.currentPage - 1)
  }
}

const handleNext = () => {
  if (props.currentPage < totalPages.value) {
    emit('page-change', props.currentPage + 1)
  }
}

const handleJumpPage = () => {
  const page = Math.max(1, Math.min(totalPages.value, inputPage.value || 1))
  inputPage.value = page
  if (page !== props.currentPage) {
    emit('page-change', page)
  }
}

const handlePageSizeChange = () => {
  emit('size-change', currentPageSize.value)
}

// 监听器
watch(() => props.currentPage, (newVal) => {
  inputPage.value = newVal
})

watch(() => props.pageSize, (newVal) => {
  currentPageSize.value = newVal
})
</script>

<style scoped>
.pagination {
  display: flex;
  flex-direction: row;
  gap: 8px;
  padding: 12px 0;
  color: var(--el-text-color-regular);
  font-size: 0.8rem;
}

/* 顶部信息区 */
.pagination-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.total-info {
  color: var(--el-text-color-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.page-size-select {
  padding: 2px 6px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 3px;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 55px;
}

.page-size-select:hover:not(:disabled) {
  border-color: var(--el-color-primary);
}

.page-size-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 控制区 */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 28px;
  border: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.75rem;
}

.pagination-btn:hover:not(.disabled):not(:disabled) {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.pagination-btn.disabled,
.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-btn i {
  font-size: 0.7rem;
}

/* 页码信息 */
.page-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  margin: 0 8px;
}

.page-input {
  width: 35px;
  height: 24px;
  padding: 2px 4px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 3px;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
  text-align: center;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.page-input:focus {
  outline: none;
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 1px rgba(64, 158, 255, 0.3);
}

.page-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.page-input::placeholder {
  color: var(--el-text-color-secondary);
}

.page-separator {
  color: var(--el-text-color-secondary);
  font-weight: 500;
  margin: 0 1px;
}

.total-pages {
  color: var(--el-text-color-secondary);
  font-weight: 500;
  min-width: 15px;
}

/* 极窄屏幕优化 */
@media (max-width: 400px) {
  .pagination {
    gap: 6px;
    padding: 8px 0;
  }
  
  .pagination-top {
    flex-direction: column;
    gap: 4px;
  }
  
  .pagination-controls {
    gap: 6px;
  }
  
  .page-info {
    margin: 0 4px;
  }
}
</style> 