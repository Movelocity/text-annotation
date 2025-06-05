<template>
  <div class="home-page">
    <el-container>
      <el-header class="header">
        <h1>文本标注系统</h1>
        <div class="header-actions">
          <el-button 
            type="primary" 
            @click="checkHealth"
            :loading="healthLoading"
          >
            检查连接
          </el-button>
          <el-button 
            @click="appStore.toggleTheme"
            :icon="appStore.theme === 'light' ? 'Moon' : 'Sunny'"
          >
            切换主题
          </el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <h3>系统统计</h3>
              </template>
              <div v-if="statsLoading" class="loading-container">
                <el-skeleton :rows="3" animated />
              </div>
              <div v-else-if="stats" class="stats-content">
                <div class="stat-item">
                  <span class="stat-label">总文本数：</span>
                  <span class="stat-value">{{ stats.total_texts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">已标注：</span>
                  <span class="stat-value success">{{ stats.labeled_texts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">未标注：</span>
                  <span class="stat-value warning">{{ stats.unlabeled_texts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">标签总数：</span>
                  <span class="stat-value">{{ stats.total_labels }}</span>
                </div>
              </div>
              <div v-else class="error-message">
                <el-alert title="无法获取统计数据" type="error" :closable="false" />
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <h3>快速操作</h3>
              </template>
              <div class="quick-actions">
                <el-button 
                  type="primary" 
                  size="large" 
                  style="width: 100%; margin-bottom: 12px;"
                  @click="loadAnnotations"
                  :loading="annotationStore.loading"
                >
                  查看标注数据
                </el-button>
                <el-button 
                  type="success" 
                  size="large" 
                  style="width: 100%; margin-bottom: 12px;"
                  @click="loadLabels"
                  :loading="labelStore.loading"
                >
                  管理标签
                </el-button>
                <el-button 
                  type="info" 
                  size="large" 
                  style="width: 100%;"
                  @click="refreshStats"
                  :loading="statsLoading"
                >
                  刷新统计
                </el-button>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <h3>标签分布</h3>
              </template>
              <div v-if="statsLoading" class="loading-container">
                <el-skeleton :rows="3" animated />
              </div>
              <div v-else-if="stats?.label_statistics.length" class="label-stats">
                <div 
                  v-for="labelStat in stats.label_statistics.slice(0, 5)" 
                  :key="labelStat.label"
                  class="label-stat-item"
                >
                  <span class="label-name">{{ labelStat.label }}</span>
                  <el-tag>{{ labelStat.count }}</el-tag>
                </div>
                <div v-if="stats.label_statistics.length > 5" class="more-labels">
                  还有 {{ stats.label_statistics.length - 5 }} 个标签...
                </div>
              </div>
              <div v-else class="no-data">
                <el-empty description="暂无标签数据" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '../stores/app'
import { useAnnotationStore } from '../stores/annotation'
import { useLabelStore } from '../stores/label'
import { statsApi, healthApi } from '../services/api'
import type { SystemStats } from '../types/api'

const appStore = useAppStore()
const annotationStore = useAnnotationStore()
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

const loadAnnotations = async () => {
  try {
    await annotationStore.searchAnnotations({ page: 1, per_page: 10 })
    ElMessage.success(`加载了 ${annotationStore.annotations.length} 条标注数据`)
  } catch (error) {
    console.error('加载标注数据失败:', error)
    ElMessage.error('加载标注数据失败')
  }
}

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

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

.header {
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header h1 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  padding: 20px;
}

.loading-container {
  padding: 20px;
}

.stats-content {
  padding: 20px 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.stat-label {
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.stat-value {
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.stat-value.success {
  color: var(--el-color-success);
}

.stat-value.warning {
  color: var(--el-color-warning);
}

.quick-actions {
  padding: 20px 0;
}

.label-stats {
  padding: 20px 0;
}

.label-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.label-name {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.more-labels {
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 12px;
}

.no-data {
  padding: 20px 0;
}

.error-message {
  padding: 20px 0;
}
</style> 