/**
 * 标注数据状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { annotationApi } from '@/services/api'
import type {
  AnnotationDataResponse,
  AnnotationDataList,
  AnnotationDataCreate,
  AnnotationDataUpdate,
  SearchRequest,
  BulkLabelRequest,
  TextImportRequest
} from '@/types/api'

export const useAnnotationStore = defineStore('annotation', () => {
  // 状态
  const annotations = ref<AnnotationDataResponse[]>([])
  const currentAnnotation = ref<AnnotationDataResponse | null>(null)
  const searchParams = ref<SearchRequest>({
    page: 1,
    per_page: 50,
    unlabeled_only: false
  })
  const total = ref(0)
  const loading = ref(false)

  // 计算属性
  const hasAnnotations = computed(() => annotations.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / searchParams.value.per_page!))

  // 方法
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const searchAnnotations = async (params?: Partial<SearchRequest>) => {
    try {
      setLoading(true)
      if (params) {
        searchParams.value = { ...searchParams.value, ...params }
      }
      const response: AnnotationDataList = await annotationApi.search(searchParams.value)
      annotations.value = response.items
      total.value = response.total
      return response
    } catch (error) {
      console.error('搜索标注数据失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const createAnnotation = async (data: AnnotationDataCreate) => {
    try {
      setLoading(true)
      const newAnnotation = await annotationApi.create(data)
      annotations.value.unshift(newAnnotation)
      total.value += 1
      return newAnnotation
    } catch (error) {
      console.error('创建标注失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const updateAnnotation = async (id: number, data: AnnotationDataUpdate) => {
    try {
      setLoading(true)
      const updatedAnnotation = await annotationApi.update(id, data)
      const index = annotations.value.findIndex(a => a.id === id)
      if (index !== -1) {
        annotations.value[index] = updatedAnnotation
      }
      if (currentAnnotation.value?.id === id) {
        currentAnnotation.value = updatedAnnotation
      }
      return updatedAnnotation
    } catch (error) {
      console.error('更新标注失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const deleteAnnotation = async (id: number) => {
    try {
      setLoading(true)
      await annotationApi.delete(id)
      annotations.value = annotations.value.filter(a => a.id !== id)
      total.value -= 1
      if (currentAnnotation.value?.id === id) {
        currentAnnotation.value = null
      }
    } catch (error) {
      console.error('删除标注失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const getAnnotation = async (id: number) => {
    try {
      setLoading(true)
      const annotation = await annotationApi.get(id)
      currentAnnotation.value = annotation
      return annotation
    } catch (error) {
      console.error('获取标注失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const bulkLabelAnnotations = async (data: BulkLabelRequest) => {
    try {
      setLoading(true)
      const result = await annotationApi.bulkLabel(data)
      // 重新搜索以更新数据
      await searchAnnotations()
      return result
    } catch (error) {
      console.error('批量标注失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const importTexts = async (data: TextImportRequest) => {
    try {
      setLoading(true)
      const result = await annotationApi.importTexts(data)
      // 重新搜索以显示新导入的数据
      await searchAnnotations()
      return result
    } catch (error) {
      console.error('导入文本失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const setCurrentAnnotation = (annotation: AnnotationDataResponse | null) => {
    currentAnnotation.value = annotation
  }

  const resetSearch = () => {
    searchParams.value = {
      page: 1,
      per_page: 50,
      unlabeled_only: false
    }
  }

  return {
    // 状态
    annotations,
    currentAnnotation,
    searchParams,
    total,
    loading,
    // 计算属性
    hasAnnotations,
    totalPages,
    // 方法
    searchAnnotations,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    getAnnotation,
    bulkLabelAnnotations,
    importTexts,
    setCurrentAnnotation,
    resetSearch,
    setLoading
  }
}) 