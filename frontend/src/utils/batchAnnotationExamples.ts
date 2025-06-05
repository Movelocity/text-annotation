/**
 * 批量标注使用示例
 * 展示如何使用批量筛选和更新标签功能
 */

import { batchApi } from '@/services/batchAnnotation'
import { annotationApi } from '@/services/api'
import type { BatchFilterOptions, BatchUpdateOptions } from '@/services/batchAnnotation'

// 示例：筛选包含"客服"关键词但不包含"测试"的文本
export async function exampleFilterCustomerService() {
  const filterOptions: BatchFilterOptions = {
    includeKeywords: ['客服'],
    excludeKeywords: ['测试'],
    page: 1,
    perPage: 50
  }

  try {
    const result = await batchApi.filter(filterOptions)
    console.log('筛选结果:', result)
    return result
  } catch (error) {
    console.error('筛选失败:', error)
    throw error
  }
}

// 示例：筛选包含"客户服务"标签但不包含"已处理"标签的文本
export async function exampleFilterByLabels() {
  const filterOptions: BatchFilterOptions = {
    includeLabels: ['客户服务'],
    excludeLabels: ['已处理'],
    page: 1,
    perPage: 100
  }

  try {
    const result = await batchApi.filter(filterOptions)
    console.log('按标签筛选结果:', result)
    return result
  } catch (error) {
    console.error('按标签筛选失败:', error)
    throw error
  }
}

// 示例：为筛选的文本批量添加"已审核"标签
export async function exampleAddReviewedLabel() {
  const filterOptions: BatchFilterOptions = {
    includeLabels: ['客户服务'],
    excludeLabels: ['已审核']
  }

  try {
    const result = await batchApi.addLabels(filterOptions, ['已审核'])
    console.log('批量添加标签结果:', result)
    return result
  } catch (error) {
    console.error('批量添加标签失败:', error)
    throw error
  }
}

// 示例：为指定ID的文本批量删除"待处理"标签
export async function exampleRemovePendingLabel() {
  const textIds = [1, 2, 3, 4, 5]

  try {
    const result = await batchApi.removeLabelsFromTexts(textIds, ['待处理'])
    console.log('批量删除标签结果:', result)
    return result
  } catch (error) {
    console.error('批量删除标签失败:', error)
    throw error
  }
}

// 示例：复杂的批量操作 - 同时添加和删除标签
export async function exampleComplexBatchUpdate() {
  const filterOptions: BatchFilterOptions = {
    includeKeywords: ['投诉'],
    includeLabels: ['客户服务'],
    excludeLabels: ['已解决']
  }

  const updateOptions: BatchUpdateOptions = {
    addLabels: ['紧急处理', '已分配'],
    removeLabels: ['待处理']
  }

  try {
    const result = await batchApi.updateByFilter(filterOptions, updateOptions)
    console.log('复杂批量更新结果:', result)
    return result
  } catch (error) {
    console.error('复杂批量更新失败:', error)
    throw error
  }
}

// 示例：预览功能 - 查看筛选结果而不执行更新
export async function examplePreviewFilter() {
  const filterOptions: BatchFilterOptions = {
    includeKeywords: ['售后'],
    unlabeledOnly: false
  }

  try {
    const result = await batchApi.preview(filterOptions)
    console.log('预览结果:', result)
    console.log(`总共将影响 ${result.totalCount} 条记录`)
    return result
  } catch (error) {
    console.error('预览失败:', error)
    throw error
  }
}

// 示例：使用高级搜索API直接搜索
export async function exampleAdvancedSearch() {
  try {
    const result = await annotationApi.advancedSearch({
      query: '退款',
      exclude_query: '测试',
      labels: '客户服务,售后',
      exclude_labels: '已关闭',
      unlabeled_only: false,
      page: 1,
      per_page: 50
    })
    console.log('高级搜索结果:', result)
    return result
  } catch (error) {
    console.error('高级搜索失败:', error)
    throw error
  }
}

// 示例：分步骤的批量标注工作流
export async function exampleBatchWorkflow() {
  console.log('开始批量标注工作流...')

  try {
    // 步骤1: 筛选待处理的客服文本
    console.log('步骤1: 筛选待处理的客服文本')
    const filterOptions: BatchFilterOptions = {
      includeKeywords: ['客服', '咨询'],
      excludeLabels: ['已处理'],
      unlabeledOnly: false
    }

    const filteredTexts = await batchApi.filter(filterOptions)
    console.log(`找到 ${filteredTexts.total} 条待处理的客服文本`)

    // 步骤2: 预览将要更新的文本
    console.log('步骤2: 预览将要更新的文本')
    const preview = await batchApi.preview(filterOptions)
    console.log(`预览前 ${preview.texts.length} 条文本:`)
    preview.texts.forEach((text, index) => {
      console.log(`${index + 1}. [${text.id}] ${text.text.substring(0, 50)}...`)
    })

    // 步骤3: 批量添加"客户服务"和"待分类"标签
    console.log('步骤3: 批量添加标签')
    const addResult = await batchApi.addLabels(filterOptions, ['客户服务', '待分类'])
    console.log(`成功为 ${addResult?.updated_count} 条文本添加标签`)

    // 步骤4: 筛选带有紧急关键词的文本
    console.log('步骤4: 筛选紧急文本')
    const urgentFilter: BatchFilterOptions = {
      includeKeywords: ['紧急', '急', '马上', '立即'],
      includeLabels: ['客户服务']
    }

    const urgentTexts = await batchApi.filter(urgentFilter)
    console.log(`找到 ${urgentTexts.total} 条紧急文本`)

    // 步骤5: 为紧急文本添加"紧急"标签并删除"待分类"标签
    console.log('步骤5: 更新紧急文本标签')
    const urgentUpdate = await batchApi.updateByFilter(urgentFilter, {
      addLabels: ['紧急'],
      removeLabels: ['待分类']
    })
    console.log(`成功更新 ${urgentUpdate?.updated_count} 条紧急文本`)

    console.log('批量标注工作流完成!')
    
    return {
      total_processed: filteredTexts.total,
      urgent_processed: urgentUpdate?.updated_count || 0
    }

  } catch (error) {
    console.error('批量标注工作流失败:', error)
    throw error
  }
}

// 导出所有示例函数
export const batchAnnotationExamples = {
  filterCustomerService: exampleFilterCustomerService,
  filterByLabels: exampleFilterByLabels,
  addReviewedLabel: exampleAddReviewedLabel,
  removePendingLabel: exampleRemovePendingLabel,
  complexBatchUpdate: exampleComplexBatchUpdate,
  previewFilter: examplePreviewFilter,
  advancedSearch: exampleAdvancedSearch,
  batchWorkflow: exampleBatchWorkflow
} 