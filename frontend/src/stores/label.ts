/**
 * 标签管理状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { labelApi } from '../services/api'
import type { LabelResponse, LabelCreate } from '../types/api'

export const useLabelStore = defineStore('label', () => {
  // 状态
  const labels = ref<LabelResponse[]>([])
  const loading = ref(false)

  // 计算属性
  const hasLabels = computed(() => labels.value.length > 0)
  const labelOptions = computed(() => 
    labels.value.map(label => ({
      value: label.label,
      label: label.label,
      id: label.id
    }))
  )

  // 方法
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const fetchLabels = async () => {
    try {
      setLoading(true)
      const labelList = await labelApi.getAll()
      labels.value = labelList
      return labelList
    } catch (error) {
      console.error('获取标签列表失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const createLabel = async (data: LabelCreate) => {
    try {
      setLoading(true)
      const newLabel = await labelApi.create(data)
      labels.value.push(newLabel)
      return newLabel
    } catch (error) {
      console.error('创建标签失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const deleteLabel = async (id: number) => {
    try {
      setLoading(true)
      await labelApi.delete(id)
      labels.value = labels.value.filter(label => label.id !== id)
    } catch (error) {
      console.error('删除标签失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const getLabelById = (id: number) => {
    return labels.value.find(label => label.id === id)
  }

  const getLabelByName = (name: string) => {
    return labels.value.find(label => label.label === name)
  }

  return {
    // 状态
    labels,
    loading,
    // 计算属性
    hasLabels,
    labelOptions,
    // 方法
    fetchLabels,
    createLabel,
    deleteLabel,
    getLabelById,
    getLabelByName,
    setLoading
  }
}) 