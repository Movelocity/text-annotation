/**
 * 标签管理状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { labelApi, statsApi } from '@/services/api'
import type { LabelResponse, LabelCreate, LabelUpdate, SystemStats, LabelStats } from '@/types/api'

export const useLabelStore = defineStore('label', () => {
  // 状态
  const labels = ref<LabelResponse[]>([])
  const loading = ref(false)
  const systemStats = ref<SystemStats | null>(null)
  const searchQuery = ref('')

  // 计算属性
  const hasLabels = computed(() => labels.value.length > 0)
  const labelOptions = computed(() => 
    labels.value.map(label => ({
      value: label.label,
      label: label.label,
      id: label.id
    }))
  )

  // 搜索过滤后的标签列表
  const filteredLabels = computed(() => {
    if (!searchQuery.value.trim()) {
      return labels.value
    }
    const query = searchQuery.value.toLowerCase()
    return labels.value.filter(label => 
      label.label.toLowerCase().includes(query) ||
      (label.description && label.description.toLowerCase().includes(query))
    )
  })

  // 标签统计信息
  const labelStatsMap = computed(() => {
    if (!systemStats.value?.label_statistics) return new Map()
    const map = new Map<string, LabelStats>()
    systemStats.value.label_statistics.forEach(stat => {
      map.set(stat.label, stat)
    })
    return map
  })

  // 按使用频率排序的标签
  const labelsByUsage = computed(() => {
    return [...filteredLabels.value].sort((a, b) => {
      const aCount = labelStatsMap.value.get(a.label)?.count || 0
      const bCount = labelStatsMap.value.get(b.label)?.count || 0
      return bCount - aCount
    })
  })

  // 未使用的标签
  const unusedLabels = computed(() => {
    return filteredLabels.value.filter(label => {
      const count = labelStatsMap.value.get(label.label)?.count || 0
      return count === 0
    })
  })

  // 统计概览
  const statsOverview = computed(() => ({
    totalLabels: labels.value.length,
    usedLabels: labels.value.length - unusedLabels.value.length,
    unusedLabels: unusedLabels.value.length,
    totalTexts: systemStats.value?.total_texts || 0,
    labeledTexts: systemStats.value?.labeled_texts || 0
  }))

  // 方法
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setSearchQuery = (query: string) => {
    searchQuery.value = query
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

  const fetchSystemStats = async () => {
    try {
      const stats = await statsApi.system()
      systemStats.value = stats
      return stats
    } catch (error) {
      console.error('获取系统统计失败:', error)
      throw error
    }
  }

  const createLabel = async (data: LabelCreate) => {
    try {
      setLoading(true)
      const newLabel = await labelApi.create(data)
      labels.value.push(newLabel)
      // 创建标签后刷新统计数据
      await fetchSystemStats()
      return newLabel
    } catch (error) {
      console.error('创建标签失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const updateLabel = async (id: number, data: LabelUpdate) => {
    try {
      setLoading(true)
      const updatedLabel = await labelApi.update(id, data)
      const index = labels.value.findIndex(label => label.id === id)
      if (index !== -1) {
        labels.value[index] = updatedLabel
      }
      // 更新标签后刷新统计数据
      await fetchSystemStats()
      return updatedLabel
    } catch (error) {
      console.error('更新标签失败:', error)
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
      // 删除标签后刷新统计数据
      await fetchSystemStats()
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

  const getLabelStats = (labelName: string): LabelStats | null => {
    return labelStatsMap.value.get(labelName) || null
  }

  // 初始化数据
  const initializeData = async () => {
    await Promise.all([
      fetchLabels(),
      fetchSystemStats()
    ])
  }

  return {
    // 状态
    labels,
    loading,
    systemStats,
    searchQuery,
    // 计算属性
    hasLabels,
    labelOptions,
    filteredLabels,
    labelsByUsage,
    unusedLabels,
    statsOverview,
    labelStatsMap,
    // 方法
    fetchLabels,
    fetchSystemStats,
    createLabel,
    updateLabel,
    deleteLabel,
    getLabelById,
    getLabelByName,
    getLabelStats,
    setLoading,
    setSearchQuery,
    initializeData
  }
}) 