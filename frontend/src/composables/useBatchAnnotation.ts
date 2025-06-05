/**
 * 批量标注 Composable
 * 提供批量筛选和更新标签的响应式状态管理
 */

import { computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { batchApi } from '@/services/batchAnnotation'
import type {
  BatchFilterOptions,
  BatchUpdateOptions
} from '@/services/batchAnnotation'
import type {
  AnnotationDataResponse,
  // BulkUpdateLabelsResponse
} from '@/types/api'

export interface BatchState {
  // 筛选条件
  filterOptions: BatchFilterOptions
  // 筛选结果
  filteredTexts: AnnotationDataResponse[]
  totalCount: number
  // 选中的文本ID
  selectedTextIds: number[]
  // 加载状态
  isLoading: boolean
  isUpdating: boolean
  // 预览模式
  isPreviewMode: boolean
}

export function useBatchAnnotation() {
  // 响应式状态
  const state = reactive<BatchState>({
    filterOptions: {
      includeKeywords: [],
      excludeKeywords: [],
      includeLabels: [],
      excludeLabels: [],
      unlabeledOnly: false,
      page: 1,
      perPage: 50
    },
    filteredTexts: [],
    totalCount: 0,
    selectedTextIds: [],
    isLoading: false,
    isUpdating: false,
    isPreviewMode: false
  })

  // 计算属性
  const hasFilterConditions = computed(() => {
    const { filterOptions } = state
    return !!(
      filterOptions.includeKeywords?.length ||
      filterOptions.excludeKeywords?.length ||
      filterOptions.includeLabels?.length ||
      filterOptions.excludeLabels?.length ||
      filterOptions.unlabeledOnly
    )
  })

  const selectedTextsCount = computed(() => state.selectedTextIds.length)

  const hasSelection = computed(() => selectedTextsCount.value > 0)

  // 筛选方法
  const filterTexts = async () => {
    if (!hasFilterConditions.value) {
      ElMessage.warning('请设置筛选条件')
      return
    }

    state.isLoading = true
    try {
      const result = await batchApi.filter(state.filterOptions)
      state.filteredTexts = result.items
      state.totalCount = result.total
      state.selectedTextIds = [] // 清空选择
      
      ElMessage.success(`找到 ${result.total} 条匹配的文本`)
    } catch (error: any) {
      ElMessage.error(`筛选失败: ${error.detail || error.message}`)
      console.error('Filter error:', error)
    } finally {
      state.isLoading = false
    }
  }

  // 预览筛选结果
  const previewFilter = async () => {
    if (!hasFilterConditions.value) {
      ElMessage.warning('请设置筛选条件')
      return
    }

    state.isLoading = true
    state.isPreviewMode = true
    try {
      const result = await batchApi.preview(state.filterOptions)
      state.filteredTexts = result.texts
      state.totalCount = result.totalCount
      state.selectedTextIds = []
      
      ElMessage.info(`预览找到 ${result.totalCount} 条匹配的文本（显示前 ${result.texts.length} 条）`)
    } catch (error: any) {
      ElMessage.error(`预览失败: ${error.detail || error.message}`)
      console.error('Preview error:', error)
    } finally {
      state.isLoading = false
    }
  }

  // 批量更新标签（通过筛选条件）
  const updateLabelsByFilter = async (updateOptions: BatchUpdateOptions) => {
    if (!hasFilterConditions.value) {
      ElMessage.warning('请设置筛选条件')
      return null
    }

    state.isUpdating = true
    try {
      const result = await batchApi.updateByFilter(state.filterOptions, updateOptions)
      ElMessage.success(result.message)
      
      // 刷新筛选结果
      await filterTexts()
      
      return result
    } catch (error: any) {
      ElMessage.error(`批量更新失败: ${error.detail || error.message}`)
      console.error('Bulk update error:', error)
      return null
    } finally {
      state.isUpdating = false
    }
  }

  // 批量更新标签（通过选中的ID）
  const updateLabelsBySelection = async (updateOptions: BatchUpdateOptions) => {
    if (!hasSelection.value) {
      ElMessage.warning('请选择要更新的文本')
      return null
    }

    state.isUpdating = true
    try {
      const result = await batchApi.updateByIds(state.selectedTextIds, updateOptions)
      ElMessage.success(result.message)
      
      // 刷新筛选结果
      await filterTexts()
      
      return result
    } catch (error: any) {
      ElMessage.error(`批量更新失败: ${error.detail || error.message}`)
      console.error('Bulk update error:', error)
      return null
    } finally {
      state.isUpdating = false
    }
  }

  // 便利方法：为筛选结果添加标签
  const addLabelsToFiltered = async (labels: string[]) => {
    return await updateLabelsByFilter({ addLabels: labels })
  }

  // 便利方法：从筛选结果删除标签
  const removeLabelsFromFiltered = async (labels: string[]) => {
    return await updateLabelsByFilter({ removeLabels: labels })
  }

  // 便利方法：为选中的文本添加标签
  const addLabelsToSelected = async (labels: string[]) => {
    return await updateLabelsBySelection({ addLabels: labels })
  }

  // 便利方法：从选中的文本删除标签
  const removeLabelsFromSelected = async (labels: string[]) => {
    return await updateLabelsBySelection({ removeLabels: labels })
  }

  // 选择管理
  const selectAll = () => {
    state.selectedTextIds = state.filteredTexts.map(text => text.id)
  }

  const clearSelection = () => {
    state.selectedTextIds = []
  }

  const toggleSelection = (textId: number) => {
    const index = state.selectedTextIds.indexOf(textId)
    if (index > -1) {
      state.selectedTextIds.splice(index, 1)
    } else {
      state.selectedTextIds.push(textId)
    }
  }

  const isSelected = (textId: number) => {
    return state.selectedTextIds.includes(textId)
  }

  // 重置状态
  const resetState = () => {
    state.filterOptions = {
      includeKeywords: [],
      excludeKeywords: [],
      includeLabels: [],
      excludeLabels: [],
      unlabeledOnly: false,
      page: 1,
      perPage: 50
    }
    state.filteredTexts = []
    state.totalCount = 0
    state.selectedTextIds = []
    state.isPreviewMode = false
  }

  // 更新筛选条件的便利方法
  const setIncludeKeywords = (keywords: string[]) => {
    state.filterOptions.includeKeywords = keywords
  }

  const setExcludeKeywords = (keywords: string[]) => {
    state.filterOptions.excludeKeywords = keywords
  }

  const setIncludeLabels = (labels: string[]) => {
    state.filterOptions.includeLabels = labels
  }

  const setExcludeLabels = (labels: string[]) => {
    state.filterOptions.excludeLabels = labels
  }

  const setUnlabeledOnly = (unlabeledOnly: boolean) => {
    state.filterOptions.unlabeledOnly = unlabeledOnly
  }

  return {
    // 状态
    state,
    
    // 计算属性
    hasFilterConditions,
    selectedTextsCount,
    hasSelection,
    
    // 筛选方法
    filterTexts,
    previewFilter,
    
    // 更新方法
    updateLabelsByFilter,
    updateLabelsBySelection,
    addLabelsToFiltered,
    removeLabelsFromFiltered,
    addLabelsToSelected,
    removeLabelsFromSelected,
    
    // 选择管理
    selectAll,
    clearSelection,
    toggleSelection,
    isSelected,
    
    // 工具方法
    resetState,
    setIncludeKeywords,
    setExcludeKeywords,
    setIncludeLabels,
    setExcludeLabels,
    setUnlabeledOnly
  }
} 