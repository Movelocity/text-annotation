<!--
  数据标注工作台
  主要功能：文本列表、文本查看、标签标注
-->
<template>
  <div class="annotation-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>数据标注工作台</h1>
        <div class="quick-stats" v-if="!annotationStore.loading">
          <el-tag type="info" size="small">
            总计：{{ annotationStore.total }} 条
          </el-tag>
          <el-tag type="success" size="small">
            已标注：{{ labeledCount }}
          </el-tag>
          <el-tag type="warning" size="small">
            未标注：{{ unlabeledCount }}
          </el-tag>
          <el-tag type="primary" size="small">
            当前：{{ currentIndex + 1 }} / {{ annotationStore.annotations.length }}
          </el-tag>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="handleRefresh" :loading="annotationStore.loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="goToHome">
          <el-icon><House /></el-icon>
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
        <div class="navigation-controls" v-if="currentItem">
          <el-button-group>
            <el-button 
              @click="handlePrevious"
              :disabled="currentIndex <= 0"
              size="small"
            >
              <el-icon><ArrowLeft /></el-icon>
              上一条
            </el-button>
            <el-button 
              @click="handleNext"
              :disabled="currentIndex >= annotationStore.annotations.length - 1"
              size="small"
            >
              下一条
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </el-button-group>
          
          <div class="position-info">
            {{ currentIndex + 1 }} / {{ annotationStore.annotations.length }}
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
import { Refresh, House, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
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
  background: var(--el-bg-color);
}

.page-header {
  flex-shrink: 0;
  padding: 16px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: var(--el-text-color-primary);
}

.quick-stats {
  display: flex;
  gap: 8px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.work-area {
  flex: 1;
  display: grid;
  grid-template-columns: 350px 1fr 400px;
  gap: 1px;
  background: var(--el-border-color-light);
  min-height: 0;
}

.left-panel,
.center-panel,
.right-panel {
  background: var(--el-bg-color);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.left-panel {
  min-width: 300px;
}

.center-panel {
  min-width: 400px;
  position: relative;
}

.right-panel {
  min-width: 350px;
}

.navigation-controls {
  position: absolute;
  bottom: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.position-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

/* 响应式布局 */
@media (max-width: 1400px) {
  .work-area {
    grid-template-columns: 300px 1fr 350px;
  }
}

@media (max-width: 1200px) {
  .work-area {
    grid-template-columns: 1fr;
    grid-template-rows: 40% 35% 25%;
  }
  
  .navigation-controls {
    position: static;
    margin-top: auto;
  }
}
</style> 