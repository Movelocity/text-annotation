<!--
  数据标注工作台
  主要功能：文本列表、文本查看、标签标注
-->
<template>
  <div class="annotation-page">
    <!-- 页面头部 -->
    <div class="page-header glass-panel">
      <div class="header-left">
        <div class="header-breadcrumb">
          <i class="fas fa-home"></i>
          <span class="breadcrumb-separator">/</span>
          <span class="current-page">标注工作台</span>
        </div>
        <h1 class="page-title">
          <i class="fas fa-magic"></i>
          数据标注工作台
        </h1>
        <div class="quick-stats" v-if="!annotationStore.loading">
          <div class="stat-badge total">
            <i class="fas fa-file-text"></i>
            <span>总计：{{ annotationStore.total }} 条</span>
          </div>
          <div class="stat-badge success">
            <i class="fas fa-check-circle"></i>
            <span>已标注：{{ labeledCount }}</span>
          </div>
          <div class="stat-badge warning">
            <i class="fas fa-clock"></i>
            <span>未标注：{{ unlabeledCount }}</span>
          </div>
          <div v-if="currentIndex >= 0" class="stat-badge primary">
            <i class="fas fa-crosshairs"></i>
            <span>当前：{{ currentIndex + 1 }} / {{ annotationStore.annotations.length }}</span>
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button 
          @click="handleRefresh" 
          :loading="annotationStore.loading"
          class="modern-btn shadow-hover"
        >
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': annotationStore.loading }"></i>
          刷新
        </el-button>
        <el-button @click="goToHome" class="modern-btn shadow-hover">
          <i class="fas fa-home"></i>
          返回首页
        </el-button>
      </div>
    </div>

    <!-- 主工作区域 -->
    <div class="work-area">
      <!-- 左侧：文本列表 -->
      <div class="left-panel">
        <TextList
          :selected-item="currentItem"
          @item-select="handleItemSelect"
        />
      </div>

      <!-- 中间：文本查看器 -->
      <div class="center-panel">
        <TextViewer :current-item="currentItem" />
        
        <!-- 导航控制 -->
        <div class="navigation-controls glass-panel" v-if="currentItem">
          <div class="nav-buttons">
            <el-button 
              @click="handlePrevious"
              :disabled="currentIndex <= 0"
              class="nav-btn shadow-hover"
              :class="{ disabled: currentIndex <= 0 }"
            >
              <i class="fas fa-chevron-left"></i>
              上一条
            </el-button>
            <el-button 
              @click="handleNext"
              :disabled="currentIndex >= annotationStore.annotations.length - 1"
              class="nav-btn shadow-hover"
              :class="{ disabled: currentIndex >= annotationStore.annotations.length - 1 }"
            >
              下一条
              <i class="fas fa-chevron-right"></i>
            </el-button>
          </div>
          
          <div class="position-info">
            <div class="position-indicator">
              <i class="fas fa-map-marker-alt"></i>
              <span class="current-position">{{ currentIndex + 1 }}</span>
              <span class="separator">/</span>
              <span class="total-count">{{ annotationStore.annotations.length }}</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${((currentIndex + 1) / annotationStore.annotations.length) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：标签选择器 -->
      <div class="right-panel">
        <LabelSelector
          :current-item="currentItem"
          @save-success="handleSaveSuccess"
          @skip="handleSkip"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnnotationStore } from '../stores/annotation'
// import { Refresh, House, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import TextList from '../components/annotation/TextList.vue'
import TextViewer from '../components/annotation/TextViewer.vue'
import LabelSelector from '../components/annotation/LabelSelector.vue'
import type { AnnotationDataResponse } from '../types/api'
import { ElMessage } from 'element-plus'

// Router
const router = useRouter()

// Stores
const annotationStore = useAnnotationStore()

// 响应式数据
const currentItem = ref<AnnotationDataResponse | null>(null)
const currentIndex = ref(-1)

// 计算属性
const labeledCount = computed(() => 
  annotationStore.annotations.filter(item => item.labels).length
)

const unlabeledCount = computed(() => 
  annotationStore.annotations.filter(item => !item.labels).length
)

// 方法
const handleItemSelect = (item: AnnotationDataResponse, index: number) => {
  currentItem.value = item
  currentIndex.value = index
}

const handlePrevious = () => {
  if (currentIndex.value > 0) {
    const newIndex = currentIndex.value - 1
    const item = annotationStore.annotations[newIndex]
    handleItemSelect(item, newIndex)
  }
}

const handleNext = () => {
  if (currentIndex.value < annotationStore.annotations.length - 1) {
    const newIndex = currentIndex.value + 1
    const item = annotationStore.annotations[newIndex]
    handleItemSelect(item, newIndex)
  }
}

const handleSaveSuccess = () => {
  ElMessage.success('标注保存成功')
  
  // 自动跳转到下一条未标注的文本
  const nextUnlabeledIndex = findNextUnlabeledIndex()
  if (nextUnlabeledIndex !== -1) {
    const item = annotationStore.annotations[nextUnlabeledIndex]
    handleItemSelect(item, nextUnlabeledIndex)
  } else {
    // 如果没有未标注的，就跳到下一条
    handleNext()
  }
}

const handleSkip = () => {
  // 跳过当前文本，移动到下一条
  const nextUnlabeledIndex = findNextUnlabeledIndex()
  if (nextUnlabeledIndex !== -1) {
    const item = annotationStore.annotations[nextUnlabeledIndex]
    handleItemSelect(item, nextUnlabeledIndex)
  } else {
    handleNext()
  }
}

const findNextUnlabeledIndex = (): number => {
  // 从当前位置之后找第一个未标注的文本
  for (let i = currentIndex.value + 1; i < annotationStore.annotations.length; i++) {
    if (!annotationStore.annotations[i].labels) {
      return i
    }
  }
  return -1
}

const handleRefresh = async () => {
  try {
    await annotationStore.searchAnnotations()
    ElMessage.success('数据刷新成功')
    
    // 清除当前选择
    currentItem.value = null
    currentIndex.value = -1
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  }
}

const goToHome = () => {
  router.push('/home')
}

// 生命周期
onMounted(async () => {
  // 如果还没有数据，先加载
  if (!annotationStore.hasAnnotations) {
    try {
      await annotationStore.searchAnnotations()
    } catch (error) {
      console.error('加载数据失败:', error)
      ElMessage.error('加载数据失败')
    }
  }

  // 自动选择第一个未标注的文本
  const firstUnlabeledIndex = annotationStore.annotations.findIndex(item => !item.labels)
  if (firstUnlabeledIndex !== -1) {
    const item = annotationStore.annotations[firstUnlabeledIndex]
    handleItemSelect(item, firstUnlabeledIndex)
  } else if (annotationStore.annotations.length > 0) {
    // 如果没有未标注的，选择第一个
    const item = annotationStore.annotations[0]
    handleItemSelect(item, 0)
  }
})
</script>

<style scoped>
.annotation-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

/* 页面头部 */
.page-header {
  flex-shrink: 0;
  padding: 20px 32px;
  margin: 16px;
  border-radius: var(--radius-lg);
  backdrop-filter: blur(20px);
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.header-left {
  flex: 1;
}

.header-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-bottom: 8px;
}

.breadcrumb-separator {
  color: var(--el-border-color);
}

.current-page {
  color: var(--el-color-primary);
  font-weight: 500;
}

.page-title {
  margin: 0 0 16px 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title i {
  color: var(--el-color-primary);
  font-size: 1.5rem;
}

.quick-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  border: 2px solid transparent;
  transition: all var(--duration-fast) ease;
}

.stat-badge.total {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: var(--shadow-sm);
}

.stat-badge.success {
  background: var(--el-color-success-light-9);
  color: var(--el-color-success-dark-2);
  border-color: var(--el-color-success-light-5);
}

.stat-badge.warning {
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning-dark-2);
  border-color: var(--el-color-warning-light-5);
}

.stat-badge.primary {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary-dark-2);
  border-color: var(--el-color-primary-light-5);
}

.stat-badge:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.header-right {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.modern-btn {
  border-radius: var(--radius-md);
  padding: 10px 16px;
  font-weight: 500;
  border: 1px solid var(--el-border-color-light);
  background: rgba(255, 255, 255, 0.9);
  transition: all var(--duration-fast) ease;
}

.modern-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  background: white;
}

.modern-btn i {
  margin-right: 6px;
}

/* 工作区域 */
.work-area {
  flex: 1;
  display: grid;
  grid-template-columns: 380px 1fr 420px;
  gap: 16px;
  padding: 0 16px 16px;
  min-height: 0;
}

.left-panel,
.center-panel,
.right-panel {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all var(--duration-normal) ease;
}

.left-panel:hover,
.center-panel:hover,
.right-panel:hover {
  box-shadow: var(--shadow-xl);
  transform: translateY(-2px);
}

.left-panel {
  min-width: 320px;
}

.center-panel {
  min-width: 400px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.right-panel {
  min-width: 380px;
}

/* 导航控制 */
.navigation-controls {
  flex-shrink: 0;
  margin: 20px;
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  backdrop-filter: blur(20px);
  box-shadow: var(--shadow-xl);
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.nav-buttons {
  display: flex;
  gap: 12px;
}

.nav-btn {
  padding: 10px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--el-border-color-light);
  background: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  transition: all var(--duration-fast) ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-btn:not(.disabled):hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  background: white;
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}

.nav-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--el-bg-color-page);
}

.position-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.position-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.position-indicator i {
  color: var(--el-color-primary);
}

.current-position {
  color: var(--el-color-primary);
  font-size: 1rem;
}

.separator {
  color: var(--el-text-color-secondary);
  margin: 0 2px;
}

.total-count {
  color: var(--el-text-color-secondary);
}

.progress-bar {
  width: 120px;
  height: 4px;
  background: var(--el-border-color-lighter);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* 响应式布局 */
@media (max-width: 1600px) {
  .work-area {
    grid-template-columns: 350px 1fr 380px;
  }
}

@media (max-width: 1400px) {
  .work-area {
    grid-template-columns: 320px 1fr 350px;
  }
  
  .page-header {
    margin: 12px;
    padding: 16px 24px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 1200px) {
  .annotation-page {
    background: var(--el-bg-color-page);
  }
  
  .work-area {
    grid-template-columns: 1fr;
    grid-template-rows: 35% 40% 25%;
  }
  
  .navigation-controls {
    position: static;
    margin: 16px;
    margin-top: auto;
  }
  
  .left-panel,
  .center-panel,
  .right-panel {
    transform: none !important;
  }
  
  .page-header {
    margin: 8px;
    padding: 12px 16px;
  }
  
  .header-left,
  .header-right {
    flex-direction: column;
    gap: 8px;
  }
  
  .quick-stats {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quick-stats {
    flex-direction: column;
  }
  
  .header-right {
    flex-direction: row;
    justify-content: space-between;
  }
  
  .navigation-controls {
    flex-direction: column;
    gap: 12px;
  }
  
  .position-info {
    align-items: center;
  }
}
</style> 