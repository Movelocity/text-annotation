/**
 * 应用状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const loading = ref(false)
  const error = ref<string | null>(null)
  const theme = ref<'light' | 'dark'>('light')

  // 计算属性
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => !!error.value)

  // 方法
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (message: string | null) => {
    error.value = message
  }

  const clearError = () => {
    error.value = null
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  return {
    // 状态
    loading,
    error,
    theme,
    // 计算属性
    isLoading,
    hasError,
    // 方法
    setLoading,
    setError,
    clearError,
    toggleTheme
  }
}) 