<!--
  现代化按钮组件
  支持自定义icon、文本、点击事件
-->
<template>
  <el-button 
    @click="handleClick"
    :loading="loading"
    :disabled="disabled"
    class="modern-btn shadow-hover"
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
interface Props {
  text?: string
  icon?: string
  loading?: boolean
  disabled?: boolean
  spinning?: boolean
  iconRight?: boolean
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
  iconRight: false
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
  padding: 10px 16px;
  font-weight: 500;
  border: 1px solid var(--el-border-color-light);
  background: rgba(255, 255, 255, 0.9);
  transition: all var(--duration-fast) ease;
}

.modern-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  background: white;
}

.modern-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--el-bg-color-page);
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
</style> 