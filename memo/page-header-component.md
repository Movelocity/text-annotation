# PageHeader 组件设计与使用指南

## 设计思路

将页面头部抽取为独立的通用组件 `PageHeader`，便于在不同页面复用，统一页面头部的设计风格和交互逻辑。

## 组件特性

- **面包屑导航**: 支持可点击的路径导航
- **页面标题**: 支持图标和标题文字
- **统计信息**: 灵活的统计数据展示，支持多种样式
- **操作按钮**: 通过 slot 支持自定义操作按钮
- **响应式设计**: 适配不同屏幕尺寸

## 使用方法

### 基本用法

```vue
<template>
  <PageHeader
    title="页面标题"
    title-icon="fas fa-magic"
    :breadcrumbs="breadcrumbs"
    :stats="headerStats"
  >
    <template #actions>
      <ModernButton text="刷新" icon="fas fa-sync-alt" @click="handleRefresh" />
      <ModernButton text="返回" icon="fas fa-arrow-left" @click="goBack" />
    </template>
  </PageHeader>
</template>

<script setup lang="ts">
import PageHeader from '@/components/common/PageHeader.vue'
import ModernButton from '@/components/common/ModernButton.vue'

// 面包屑配置
const breadcrumbs = [
  { text: '首页', to: '/home' },  // 可点击跳转
  { text: '当前页面' }             // 不可点击
]

// 统计数据配置
const headerStats = computed(() => [
  {
    key: 'total',
    label: '总计',
    value: '100 条',
    type: 'total',
    icon: 'fas fa-file-text'
  },
  {
    key: 'success',
    label: '成功',
    value: 80,
    type: 'success',
    icon: 'fas fa-check-circle'
  }
])
</script>
```

### Props 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 页面标题 |
| titleIcon | string | 否 | 标题图标 (FontAwesome 类名) |
| breadcrumbs | BreadcrumbItem[] | 否 | 面包屑导航数组 |
| stats | StatItem[] | 否 | 统计信息数组 |

### 数据类型

```typescript
interface BreadcrumbItem {
  text: string    // 显示文字
  to?: string     // 跳转路径，可选
}

interface StatItem {
  key: string                   // 唯一标识
  label: string                 // 标签文字
  value: string | number        // 统计值
  type?: 'total' | 'success' | 'warning' | 'primary' | 'info' | 'danger' | 'default'  // 样式类型
  icon?: string                 // 图标类名
}
```

### Slots

| 插槽名 | 说明 |
|--------|------|
| actions | 右侧操作按钮区域 |

## 样式系统

### 统计项样式类型

- `total`: 渐变背景，适合总数统计
- `success`: 绿色系，适合成功/完成状态
- `warning`: 橙色系，适合警告/待处理状态  
- `primary`: 蓝色系，适合主要信息
- `info`: 灰蓝色系，适合一般信息
- `danger`: 红色系，适合错误/危险状态
- `default`: 默认样式

### 响应式断点

- `1400px` 及以下：调整间距和字体大小
- `1200px` 及以下：布局调整为垂直方向
- `768px` 及以下：移动端优化布局

## 迁移指南

### 从原有页面头部迁移

1. 引入 PageHeader 组件
2. 配置 breadcrumbs 数组
3. 配置 stats 数组
4. 将操作按钮移至 actions slot
5. 删除原有的页面头部 HTML 和 CSS

### 示例：AnnotationPage 迁移

```vue
<!-- 迁移前 -->
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
    <!-- 统计信息 -->
  </div>
  <div class="header-right">
    <!-- 操作按钮 -->
  </div>
</div>

<!-- 迁移后 -->
<PageHeader
  title="数据标注工作台"
  title-icon="fas fa-magic"
  :breadcrumbs="[{ text: '标注工作台' }]"
  :stats="headerStats"
>
  <template #actions>
    <!-- 操作按钮 -->
  </template>
</PageHeader>
```

## 优势

1. **代码复用**: 减少重复的头部代码
2. **统一体验**: 保持各页面头部样式一致性  
3. **易于维护**: 头部功能集中管理
4. **配置灵活**: 支持不同页面的个性化需求
5. **类型安全**: TypeScript 类型约束，减少错误

## 扩展建议

后续可以考虑扩展的功能：

- 添加搜索框支持
- 添加用户头像/菜单
- 支持主题切换按钮
- 添加国际化支持
- 支持自定义背景和样式主题 