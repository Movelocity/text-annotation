<!--
  通用页面头部组件
  支持面包屑导航、页面标题、统计信息展示和操作按钮
-->
<template>
  <div class="page-header glass-panel">
    <div class="header-left">
      <!-- 面包屑导航 -->
      <div class="header-breadcrumb">
        <i 
          class="fas fa-home home-icon" 
          :class="{ 'clickable': props.homeRoute }"
          @click="handleHomeClick"
          :title="props.homeRoute ? '返回首页' : ''"
        ></i>
        <template v-for="(crumb, index) in (breadcrumbs || [])" :key="index">
          <span class="breadcrumb-separator">/</span>
          <span 
            :class="{ 'current-page': index === (breadcrumbs || []).length - 1 }"
            @click="crumb.to && handleBreadcrumbClick(crumb.to)"
            :style="{ cursor: crumb.to ? 'pointer' : 'default' }"
          >
            {{ crumb.text }}
          </span>
        </template>
      </div>
      
      <!-- 页面标题 -->
      <h1 class="page-title">
        <i :class="titleIcon" v-if="titleIcon"></i>
        {{ title }}
      </h1>
      
      <!-- 统计信息 -->
      <div class="quick-stats" v-if="stats && stats.length > 0">
        <div 
          v-for="stat in stats" 
          :key="stat.key"
          :class="['stat-badge', stat.type || 'default']"
        >
          <i :class="stat.icon" v-if="stat.icon"></i>
          <span>{{ stat.label }}：{{ stat.value }}</span>
        </div>
      </div>
    </div>
    
    <!-- 右侧操作按钮 -->
    <div class="header-right" v-if="$slots.actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

// 定义接口
interface BreadcrumbItem {
  text: string
  to?: string
}

interface StatItem {
  key: string
  label: string
  value: string | number
  type?: 'total' | 'success' | 'warning' | 'primary' | 'info' | 'danger' | 'default'
  icon?: string
}

// Props
const props = defineProps<{
  title: string
  titleIcon?: string
  breadcrumbs?: BreadcrumbItem[]
  stats?: StatItem[]
  homeRoute?: string // 首页路由，如果提供则home icon可点击
}>()

// Router
const router = useRouter()

// 方法
const handleBreadcrumbClick = (to: string) => {
  router.push(to)
}

const handleHomeClick = () => {
  if (props.homeRoute) {
    router.push(props.homeRoute)
  }
}
</script>

<style scoped>
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

.header-breadcrumb span:not(.breadcrumb-separator):not(.current-page):hover {
  color: var(--el-color-primary);
  transition: color 0.2s ease;
}

.home-icon {
  transition: all 0.2s ease;
}

.home-icon.clickable {
  cursor: pointer;
  color: var(--el-color-primary);
}

.home-icon.clickable:hover {
  color: var(--el-color-primary-dark-2);
  transform: scale(1.1);
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

.stat-badge.info {
  background: var(--el-color-info-light-9);
  color: var(--el-color-info-dark-2);
  border-color: var(--el-color-info-light-5);
}

.stat-badge.danger {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger-dark-2);
  border-color: var(--el-color-danger-light-5);
}

.stat-badge.default {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-primary);
  border-color: var(--el-border-color-light);
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

/* 响应式布局 */
@media (max-width: 1400px) {
  .page-header {
    margin: 12px;
    padding: 16px 24px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 1200px) {
  .header-left,
  .header-right {
    flex-direction: column;
    gap: 8px;
  }
  
  .quick-stats {
    justify-content: flex-start;
  }
  
  .page-header {
    margin: 8px;
    padding: 12px 16px;
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
}
</style> 