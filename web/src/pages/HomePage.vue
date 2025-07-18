<template>
  <div class="home-page">
    <div class="hero-section">
      <!-- Hero Content -->
      <div class="hero-content">
        <h1 class="gradient-text">文本标注系统</h1>
        <p class="hero-subtitle">高效、准确、智能的数据标注工作平台</p>
        
        <!-- 集成的数据展示部分 -->
        <div class="integrated-stats">
          <div class="stat-pill">
            <i class="fas fa-file-alt"></i>
            <span class="stat-value">{{ stats?.total_texts || 0 }}</span>
            <span class="stat-label">文档总数</span>
          </div>
          <div class="stat-pill">
            <i class="fas fa-tag"></i>
            <span class="stat-value">{{ stats?.total_labels || 0 }}</span>
            <span class="stat-label">标签总数</span>
          </div>
          <div class="stat-pill">
            <i class="fas fa-check-circle"></i>
            <span class="stat-value">{{ stats?.labeled_texts || 0 }}</span>
            <span class="stat-label">已完成</span>
          </div>
          <div class="stat-pill">
            <i class="fas fa-clock"></i>
            <span class="stat-value">{{ stats?.unlabeled_texts || 0 }}</span>
            <span class="stat-label">待处理</span>
          </div>
        </div>
        
        <!-- 快捷操作按钮组 -->
        <div class="hero-actions">
          <button class="hero-btn primary" @click="goToAnnotation">
            <i class="fas fa-tag"></i> 开始标注
          </button>
          <button class="hero-btn secondary" @click="refreshStats">
            <i class="fas fa-sync-alt"></i> 刷新数据
          </button>
        </div>
      </div>
      
      <div class="floating-icons">
        <div class="icon-item" style="animation-delay: 0s;"><i class="fas fa-brain"></i></div>
        <div class="icon-item" style="animation-delay: 0.5s;"><i class="fas fa-tags"></i></div>
        <div class="icon-item" style="animation-delay: 1s;"><i class="fas fa-chart-line"></i></div>
        <div class="icon-item" style="animation-delay: 1.5s;"><i class="fas fa-magic"></i></div>
      </div>
    </div>
    
    <!-- 简化的内容区域 -->
    <div class="content-section">
      <div class="main-content">
        <!-- 功能快捷入口 -->
        <div class="action-shortcuts">
          <h2 class="section-title">快捷功能</h2>
          <div class="shortcuts-grid">
            <div class="shortcut-item" @click="goToAnnotation">
              <div class="shortcut-icon"><i class="fas fa-tag"></i></div>
              <div class="shortcut-text">
                <h3>逐条标注</h3>
                <p>对单个文本进行精细标注</p>
              </div>
            </div>
            <div class="shortcut-item" @click="goToBatchAnnotation">
              <div class="shortcut-icon"><i class="fas fa-layer-group"></i></div>
              <div class="shortcut-text">
                <h3>批量标注</h3>
                <p>快速处理多个文本</p>
              </div>
            </div>
            <div class="shortcut-item" @click="goToLabelManage">
              <div class="shortcut-icon"><i class="fas fa-tags"></i></div>
              <div class="shortcut-text">
                <h3>标签管理</h3>
                <p>创建和管理标注标签</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { statsApi } from '@/services/api'
import type { SystemStats } from '@/types/api'

const router = useRouter()
const stats = ref<SystemStats | null>(null)
const statsLoading = ref(false)


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

const refreshStats = async () => {
  await loadStats()
  ElMessage.success('统计数据已刷新')
}

const goToAnnotation = () => {
  router.push('/pages/annotation')
}

const goToBatchAnnotation = () => {
  router.push('/pages/batch-annotation')
}

const goToLabelManage = () => {
  router.push('/pages/label-manage')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

/* Hero Section */
.hero-section {
  /* padding: 0 0 60px; */
  padding: 0 0 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
  height: 55vh;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Hero Content */
.hero-content {
  padding: 80px 20px 0;
}

.hero-content h1 {
  font-size: 3.5rem;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 50%, #e8f0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  text-shadow: none;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
  position: relative;
}

.hero-content h1::before {
  content: "智能文本标注系统";
  position: absolute;
  top: 0;
  left: 0;
  z-index: -1;
  color: white;
  font-weight: 700;
  filter: blur(1px);
  opacity: 0.8;
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

/* Content Section - smooth transition from hero */
.content-section {
  background: linear-gradient(to bottom, 
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 30%,
    rgba(255, 255, 255, 0.8) 60%,
    #ffffff 100%
  );
  position: relative;
  z-index: 1;
  margin-top: -60px;
  padding-top: 60px;
}

/* Main Content */
.main-content {
  padding: 40px 32px;
  position: relative;
  z-index: 1;
  background: transparent;
}

/* Card Styles */
.stat-card, .action-card, .label-card {
  padding: 24px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-lg);
  transition: all var(--duration-normal) ease;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
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
  background: var(--el-bg-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  border: 2px solid transparent;
}

.action-item:hover {
  transform: translateX(8px);
  box-shadow: var(--shadow-md);
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
    padding: 0 0 80px;
  }
  
  .hero-content {
    padding: 40px 20px 0;
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
  
  .hero-header {
    padding: 16px;
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

/* 集成的数据展示样式 */
.integrated-stats {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
  margin: 32px auto;
  max-width: 800px;
}

.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  min-width: 120px;
}

.stat-pill:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.stat-pill i {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
}

.stat-pill .stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
}

.stat-pill .stat-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;
}

/* 修改现有的hero-actions样式 */
.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.hero-btn {
  padding: 14px 28px;
  font-size: 16px;
  border-radius: 12px;
  border: none;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-btn.primary {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  box-shadow: 0 8px 16px rgba(238, 90, 82, 0.3);
}

.hero-btn.secondary {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.hero-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
}

/* 功能快捷入口 */
.action-shortcuts {
  padding: 40px 0;
}

.section-title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 32px;
  color: #333;
  font-weight: 600;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.shortcut-item {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  cursor: pointer;
}

.shortcut-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
}

.shortcut-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  flex-shrink: 0;
}

.shortcut-icon i {
  font-size: 24px;
  color: white;
}

.shortcut-text h3 {
  margin: 0 0 6px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.shortcut-text p {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .integrated-stats {
    gap: 12px;
    margin: 24px auto;
  }
  
  .stat-pill {
    padding: 10px 16px;
    min-width: 100px;
  }
  
  .stat-pill .stat-value {
    font-size: 1.5rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-btn {
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }
}
</style> 