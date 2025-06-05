<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="gradient-text">智能文本标注系统</h1>
        <p class="hero-subtitle">高效、准确、智能的数据标注工作平台</p>
        <div class="hero-actions">
          <el-button 
            type="primary" 
            size="large"
            @click="goToAnnotation"
            class="hero-btn transform-hover"
          >
            <i class="fas fa-rocket"></i>
            立即开始标注
          </el-button>
        </div>
      </div>
      <div class="floating-icons">
        <div class="icon-item" style="animation-delay: 0s;"><i class="fas fa-brain"></i></div>
        <div class="icon-item" style="animation-delay: 0.5s;"><i class="fas fa-tags"></i></div>
        <div class="icon-item" style="animation-delay: 1s;"><i class="fas fa-chart-line"></i></div>
        <div class="icon-item" style="animation-delay: 1.5s;"><i class="fas fa-magic"></i></div>
      </div>
    </div>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <div class="breadcrumb">
            <i class="fas fa-home"></i>
            <span>控制台</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button 
            @click="checkHealth"
            :loading="healthLoading"
            class="modern-btn shadow-hover"
          >
            <div class="status-indicator" :class="healthLoading ? 'warning pulse' : 'success'"></div>
            检查连接
          </el-button>
          <el-button 
            @click="appStore.toggleTheme"
            :icon="appStore.theme === 'light' ? 'Moon' : 'Sunny'"
            class="modern-btn shadow-hover"
          >
            切换主题
          </el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <el-row :gutter="24">
          <el-col :span="8">
            <div class="stat-card modern-card transform-hover">
              <div class="card-header">
                <div class="card-icon stats-icon">
                  <i class="fas fa-chart-bar"></i>
                </div>
                <h3>系统统计</h3>
              </div>
              <div v-if="statsLoading" class="loading-container">
                <div class="loading-spinner"></div>
                <p>加载统计数据中...</p>
              </div>
              <div v-else-if="stats" class="stats-content">
                <div class="stat-item">
                  <div class="stat-icon">
                    <i class="fas fa-file-text"></i>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ stats.total_texts }}</span>
                    <span class="stat-label">总文本数</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon success">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value success">{{ stats.labeled_texts }}</span>
                    <span class="stat-label">已标注</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon warning">
                    <i class="fas fa-clock"></i>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value warning">{{ stats.unlabeled_texts }}</span>
                    <span class="stat-label">待标注</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon primary">
                    <i class="fas fa-tags"></i>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ stats.total_labels }}</span>
                    <span class="stat-label">标签总数</span>
                  </div>
                </div>
              </div>
              <div v-else class="error-message">
                <el-alert title="无法获取统计数据" type="error" :closable="false" />
              </div>
            </div>
          </el-col>
          
          <el-col :span="8">
            <div class="action-card modern-card transform-hover">
              <div class="card-header">
                <div class="card-icon action-icon">
                  <i class="fas fa-bolt"></i>
                </div>
                <h3>快速操作</h3>
              </div>
              <div class="quick-actions">
                <div class="action-item" @click="goToAnnotation">
                  <div class="action-icon-wrapper primary">
                    <i class="fas fa-edit"></i>
                  </div>
                  <div class="action-content">
                    <h4>开始标注</h4>
                    <p>进入标注工作台开始数据标注</p>
                  </div>
                  <div class="action-arrow">
                    <i class="fas fa-chevron-right"></i>
                  </div>
                </div>
                
                <div class="action-item" @click="loadLabels">
                  <div class="action-icon-wrapper success">
                    <i class="fas fa-tags"></i>
                  </div>
                  <div class="action-content">
                    <h4>管理标签</h4>
                    <p>创建、编辑和管理标签分类</p>
                  </div>
                  <div class="action-arrow">
                    <i class="fas fa-chevron-right"></i>
                  </div>
                </div>
                
                <div class="action-item" @click="refreshStats">
                  <div class="action-icon-wrapper info">
                    <i class="fas fa-sync-alt" :class="{ 'fa-spin': statsLoading }"></i>
                  </div>
                  <div class="action-content">
                    <h4>刷新统计</h4>
                    <p>更新系统数据统计信息</p>
                  </div>
                  <div class="action-arrow">
                    <i class="fas fa-chevron-right"></i>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
          
          <el-col :span="8">
            <div class="label-card modern-card transform-hover">
              <div class="card-header">
                <div class="card-icon label-icon">
                  <i class="fas fa-chart-pie"></i>
                </div>
                <h3>标签分布</h3>
              </div>
              <div v-if="statsLoading" class="loading-container">
                <div class="loading-spinner"></div>
                <p>加载标签数据中...</p>
              </div>
              <div v-else-if="stats?.label_statistics.length" class="label-stats">
                <div 
                  v-for="(labelStat, index) in stats.label_statistics.slice(0, 5)" 
                  :key="labelStat.label"
                  class="label-stat-item"
                  :style="{ animationDelay: `${index * 0.1}s` }"
                >
                  <div class="label-info">
                    <span class="label-name">{{ labelStat.label }}</span>
                    <div class="label-progress">
                      <div 
                        class="progress-bar" 
                        :style="{ 
                          width: `${(labelStat.count / Math.max(...stats.label_statistics.map(s => s.count))) * 100}%`,
                          background: `hsl(${index * 60}, 70%, 60%)`
                        }"
                      ></div>
                    </div>
                  </div>
                  <div class="label-count">
                    <span class="count-number">{{ labelStat.count }}</span>
                  </div>
                </div>
                <div v-if="stats.label_statistics.length > 5" class="more-labels">
                  <i class="fas fa-plus-circle"></i>
                  还有 {{ stats.label_statistics.length - 5 }} 个标签
                </div>
              </div>
              <div v-else class="no-data">
                <div class="empty-state">
                  <i class="fas fa-chart-pie"></i>
                  <p>暂无标签数据</p>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// import { EditPen } from '@element-plus/icons-vue'
import { useAppStore } from '../stores/app'
// import { useAnnotationStore } from '../stores/annotation'
import { useLabelStore } from '../stores/label'
import { statsApi, healthApi } from '../services/api'
import type { SystemStats } from '../types/api'

const router = useRouter()
const appStore = useAppStore()
// const annotationStore = useAnnotationStore()
const labelStore = useLabelStore()

const stats = ref<SystemStats | null>(null)
const statsLoading = ref(false)
const healthLoading = ref(false)

const loadStats = async () => {
  try {
    statsLoading.value = true
    const response = await statsApi.system()
    stats.value = response
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    statsLoading.value = false
  }
}

const checkHealth = async () => {
  try {
    healthLoading.value = true
    await healthApi.check()
    ElMessage.success('后端连接正常')
  } catch (error) {
    console.error('健康检查失败:', error)
    ElMessage.error('后端连接失败')
  } finally {
    healthLoading.value = false
  }
}

// const loadAnnotations = async () => {
//   try {
//     await annotationStore.searchAnnotations({ page: 1, per_page: 10 })
//     ElMessage.success(`加载了 ${annotationStore.annotations.length} 条标注数据`)
//   } catch (error) {
//     console.error('加载标注数据失败:', error)
//     ElMessage.error('加载标注数据失败')
//   }
// }

const loadLabels = async () => {
  try {
    await labelStore.fetchLabels()
    ElMessage.success(`加载了 ${labelStore.labels.length} 个标签`)
  } catch (error) {
    console.error('加载标签失败:', error)
    ElMessage.error('加载标签失败')
  }
}

const refreshStats = async () => {
  await loadStats()
  ElMessage.success('统计数据已刷新')
}

const goToAnnotation = () => {
  router.push('/annotation')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

/* Hero Section */
.hero-section {
  padding: 80px 20px 120px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-content h1 {
  font-size: 3.5rem;
  margin-bottom: 20px;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 40px;
  font-weight: 300;
}

.hero-actions {
  margin-top: 40px;
}

.hero-btn {
  padding: 16px 32px;
  font-size: 18px;
  border-radius: var(--radius-lg);
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  border: none;
  color: white;
  box-shadow: var(--shadow-lg);
  transition: all var(--duration-normal) ease;
}

.hero-btn:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-xl);
}

.hero-btn i {
  margin-right: 8px;
}

/* Floating Icons */
.floating-icons {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.icon-item {
  position: absolute;
  color: rgba(255, 255, 255, 0.1);
  font-size: 2rem;
  animation: float 6s ease-in-out infinite;
}

.icon-item:nth-child(1) { top: 20%; left: 10%; }
.icon-item:nth-child(2) { top: 30%; right: 15%; }
.icon-item:nth-child(3) { bottom: 40%; left: 20%; }
.icon-item:nth-child(4) { bottom: 20%; right: 10%; }

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-20px) rotate(5deg); }
  66% { transform: translateY(10px) rotate(-5deg); }
}

/* Header */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  box-shadow: var(--shadow-sm);
}

.header-left .breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.modern-btn {
  border-radius: var(--radius-md);
  border: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  transition: all var(--duration-fast) ease;
}

.modern-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Main Content */
.main-content {
  padding: 40px 32px;
  position: relative;
  z-index: 1;
}

/* Card Styles */
.stat-card, .action-card, .label-card {
  padding: 24px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-lg);
  transition: all var(--duration-normal) ease;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--el-border-color-lighter);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
  color: white;
  box-shadow: var(--shadow-md);
}

.stats-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.action-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.label-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
}

/* Stats Content */
.stats-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) ease;
}

.stat-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  background: var(--el-color-info);
  color: white;
  font-size: 16px;
}

.stat-icon.success {
  background: var(--el-color-success);
}

.stat-icon.warning {
  background: var(--el-color-warning);
}

.stat-icon.primary {
  background: var(--el-color-primary);
}

.stat-info {
  flex: 1;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
  color: var(--el-text-color-primary);
}

.stat-value.success {
  color: var(--el-color-success);
}

.stat-value.warning {
  color: var(--el-color-warning);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

/* Action Items */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: var(--el-bg-color-page);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  border: 2px solid transparent;
}

.action-item:hover {
  transform: translateX(8px);
  box-shadow: var(--shadow-md);
  border-color: var(--el-color-primary-light-7);
}

.action-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: white;
  font-size: 18px;
}

.action-icon-wrapper.primary {
  background: var(--el-color-primary);
}

.action-icon-wrapper.success {
  background: var(--el-color-success);
}

.action-icon-wrapper.info {
  background: var(--el-color-info);
}

.action-content {
  flex: 1;
}

.action-content h4 {
  margin: 0 0 4px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.action-content p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.action-arrow {
  color: var(--el-text-color-secondary);
  font-size: 16px;
  transition: all var(--duration-fast) ease;
}

.action-item:hover .action-arrow {
  color: var(--el-color-primary);
  transform: translateX(4px);
}

/* Label Stats */
.label-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.label-stat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) ease;
  animation: slideInUp 0.5s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.label-stat-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.label-info {
  flex: 1;
}

.label-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.label-progress {
  height: 6px;
  background: var(--el-border-color-lighter);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease-out;
}

.label-count {
  margin-left: 12px;
}

.count-number {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.more-labels {
  text-align: center;
  padding: 12px;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
  border: 2px dashed var(--el-border-color);
  border-radius: var(--radius-md);
  background: var(--el-bg-color-page);
}

.more-labels i {
  margin-right: 8px;
}

/* Loading and Empty States */
.loading-container {
  text-align: center;
  padding: 40px 20px;
}

.loading-container p {
  margin-top: 16px;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-secondary);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-state p {
  font-size: 0.875rem;
  margin: 0;
}

.error-message {
  padding: 20px 0;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .hero-content h1 {
    font-size: 2.5rem;
  }
  
  .main-content {
    padding: 24px 20px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px 80px;
  }
  
  .hero-content h1 {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-btn {
    padding: 12px 24px;
    font-size: 16px;
  }
  
  .header {
    padding: 0 16px;
  }
  
  .main-content {
    padding: 20px 16px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-icon {
    margin-right: 0;
    margin-bottom: 8px;
  }
}
</style> 