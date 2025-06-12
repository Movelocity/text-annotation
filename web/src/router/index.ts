/**
 * Vue Router 配置
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/pages/home'
  },
  {
    path: '/pages/home',
    name: 'Home',
    component: () => import('@/pages/HomePage.vue'),
    meta: {
      title: '文本标注 - 首页'
    }
  },
  {
    path: '/pages/annotation',
    name: 'Annotation',
    component: () => import('@/pages/AnnotationPage.vue'),
    meta: {
      title: '数据标注工作台'
    }
  },
  {
    path: '/pages/batch-annotation',
    name: 'BatchAnnotation',
    component: () => import('@/pages/BatchAnnotationPage.vue'),
    meta: {
      title: '批量标注工具'
    }
  },
  {
    path: '/pages/label-manage',
    name: 'LabelManage',
    component: () => import('@/pages/LabelManagePage.vue'),
    meta: {
      title: '标签管理'
    }
  },
  {
    path: '/pages/data-import',
    name: 'DataImport',
    component: () => import('@/pages/DataImportPage.vue'),
    meta: {
      title: '数据导入'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to) => {
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
})

export default router 