<!--
  数据标注工作台
  主要功能：文本列表、文本查看、标签标注
-->
<template>
  <div class="annotation-page">
    <!-- 页面头部 -->


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
            <ModernButton
              text="上一条"
              icon="fas fa-chevron-left"
              :disabled="currentIndex <= 0"
              @click="handlePrevious"
            />
            <ModernButton
              text="下一条"
              icon="fas fa-chevron-right"
              :icon-right="true"
              :disabled="currentIndex >= annotationStore.annotations.length - 1"
              @click="handleNext"
            />
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnnotationStore } from '../stores/annotation'
// import { Refresh, House, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import TextList from '../components/annotation/TextList.vue'
import TextViewer from '../components/annotation/TextViewer.vue'
import LabelSelector from '../components/annotation/LabelSelector.vue'
import ModernButton from '../components/common/ModernButton.vue'
// import PageHeader from '../components/common/PageHeader.vue'
import type { AnnotationDataResponse } from '../types/api'
import { ElMessage } from 'element-plus'

// Router
const router = useRouter()

// Stores
const annotationStore = useAnnotationStore()

// 响应式数据
const currentItem = ref<AnnotationDataResponse | null>(null)
const currentIndex = ref(-1)

// 面包屑导航配置
// const breadcrumbs = [
//   { text: '标注工作台' }
// ]

// // 计算属性
// const labeledCount = computed(() => 
//   annotationStore.annotations.filter(item => item.labels).length
// )

// const unlabeledCount = computed(() => 
//   annotationStore.annotations.filter(item => !item.labels).length
// )

// // 定义统计项类型
// interface StatItem {
//   key: string
//   label: string
//   value: string | number
//   type?: 'total' | 'success' | 'warning' | 'primary' | 'info' | 'danger' | 'default'
//   icon?: string
// }

// 头部统计信息
// const headerStats = computed<StatItem[]>(() => {
//   if (annotationStore.loading) return []
  
//   const stats: StatItem[] = [
//     {
//       key: 'total',
//       label: '总计',
//       value: `${annotationStore.total} 条`,
//       type: 'total',
//       icon: 'fas fa-file-text'
//     },
//     {
//       key: 'labeled',
//       label: '已标注',
//       value: labeledCount.value,
//       type: 'success',
//       icon: 'fas fa-check-circle'
//     },
//     {
//       key: 'unlabeled',
//       label: '未标注',
//       value: unlabeledCount.value,
//       type: 'warning',
//       icon: 'fas fa-clock'
//     }
//   ]
  
//   // 如果当前有选中项，添加当前位置信息
//   if (currentIndex.value >= 0) {
//     stats.push({
//       key: 'current',
//       label: '当前',
//       value: `${currentIndex.value + 1} / ${annotationStore.annotations.length}`,
//       type: 'primary',
//       icon: 'fas fa-crosshairs'
//     })
//   }
  
//   return stats
// })

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

// const handleRefresh = async () => {
//   try {
//     await annotationStore.searchAnnotations()
//     ElMessage.success('数据刷新成功')
    
//     // 清除当前选择
//     currentItem.value = null
//     currentIndex.value = -1
//   } catch (error) {
//     console.error('刷新失败:', error)
//     ElMessage.error('刷新失败')
//   }
// }

// 生命周期
onMounted(async () => {
  // 检查URL参数
  const route = router.currentRoute.value
  const labelParam = route.query.label as string
  
     // 如果有标签参数，优先进行标签搜索
   if (labelParam) {
     try {
       await annotationStore.searchAnnotations({
         labels: labelParam,
         page: 1,
         per_page: 50
       })
       ElMessage.success(`已筛选标签"${labelParam}"的数据`)
       
       // 清除URL参数，避免刷新时重复搜索
       router.replace({ path: '/annotation' })
     } catch (error) {
       console.error('标签搜索失败:', error)
       ElMessage.error('标签搜索失败')
     }
  } else {
    // 如果还没有数据，先加载
    if (!annotationStore.hasAnnotations) {
      try {
        await annotationStore.searchAnnotations()
      } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('加载数据失败')
      }
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
  height: calc(100vh - 55px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

/* 工作区域 */
.work-area {
  flex: 1;
  display: grid;
  grid-template-columns: 380px 1fr 420px;
  gap: 16px;
  padding: 16px;
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
  /* transform: translateY(-2px); */
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
}

@media (max-width: 768px) {
  .navigation-controls {
    flex-direction: column;
    gap: 12px;
  }
  
  .position-info {
    align-items: center;
  }
}
</style> 