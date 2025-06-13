<!--
  现代化按钮组件
  支持自定义icon、文本、点击事件、尺寸、风格
-->
<template>
  <el-button 
    @click="handleClick"
    :loading="loading"
    :disabled="disabled"
    :class="[
      'modern-btn', 
      'shadow-hover',
      `modern-btn--${size}`,
      `modern-btn--${variant}`
    ]"
  >
    <i 
      v-if="icon && !loading && !iconRight" 
      :class="[icon, { 'fa-spin': spinning }]"
    ></i>
    <span v-if="text">{{ text }}</span>
    <i 
      v-if="icon && !loading && iconRight" 
      :class="[icon, { 'fa-spin': spinning }]"
    ></i>
  </el-button>
</template>

<script setup lang="ts">
type ButtonSize = 'small' | 'medium' | 'large'
type ButtonVariant = 'default' | 'primary' | 'danger' | 'prominent'

interface Props {
  text?: string
  icon?: string
  loading?: boolean
  disabled?: boolean
  spinning?: boolean
  iconRight?: boolean
  size?: ButtonSize
  variant?: ButtonVariant
}

interface Emits {
  (e: 'click'): void
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  icon: '',
  loading: false,
  disabled: false,
  spinning: false,
  iconRight: false,
  size: 'medium',
  variant: 'default'
})

const emit = defineEmits<Emits>()

const handleClick = () => {
  if (!props.loading && !props.disabled) {
    emit('click')
  }
}
</script>

<style scoped>
.modern-btn {
  border-radius: var(--radius-md);
  font-weight: 500;
  border: 1px solid;
  transition: all var(--duration-fast) ease;
}

/* 风格样式 */
.modern-btn--default {
  border-color: var(--el-border-color-light);
  background: rgba(255, 255, 255, 0.9);
  color: var(--el-text-color-primary);
}

.modern-btn--default:hover:not(:disabled) {
  background: white;
  border-color: var(--el-border-color);
}

.modern-btn--primary {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary);
  color: white;
}

.modern-btn--primary:hover:not(:disabled) {
  background: var(--el-color-primary-light-3);
  border-color: var(--el-color-primary-light-3);
}

.modern-btn--danger {
  border-color: var(--el-color-danger);
  background: var(--el-color-danger);
  color: white;
}

.modern-btn--danger:hover:not(:disabled) {
  background: var(--el-color-danger-light-3);
  border-color: var(--el-color-danger-light-3);
}

.modern-btn--prominent {
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modern-btn--prominent:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c90ff 0%, #8b5fbf 100%);
  transform: translateY(-3px);
}

/* 尺寸样式 */
.modern-btn--small {
  padding: 6px 12px;
  font-size: 12px;
  min-height: 28px;
}

.modern-btn--medium {
  padding: 10px 16px;
  font-size: 14px;
  min-height: 36px;
}

.modern-btn--large {
  padding: 14px 20px;
  font-size: 16px;
  min-height: 44px;
}

.modern-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.modern-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--el-bg-color-page) !important;
  border-color: var(--el-border-color-lighter) !important;
  color: var(--el-text-color-disabled) !important;
}

.modern-btn i {
  margin-right: 6px;
}

.modern-btn i:last-child {
  margin-right: 0;
  margin-left: 6px;
}

.modern-btn i:only-child {
  margin: 0;
}

/* 小尺寸图标间距调整 */
.modern-btn--small i {
  margin-right: 4px;
}

.modern-btn--small i:last-child {
  margin-right: 0;
  margin-left: 4px;
}

/* 大尺寸图标间距调整 */
.modern-btn--large i {
  margin-right: 8px;
}

.modern-btn--large i:last-child {
  margin-right: 0;
  margin-left: 8px;
}
</style> 