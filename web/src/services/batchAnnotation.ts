/**
 * 批量标注服务
 * 提供批量筛选和更新标签的便利方法
 */

import { annotationApi } from '@/services/api'
import type {
  AdvancedSearchRequest,
  BulkUpdateLabelsRequest,
  BulkUpdateLabelsResponse,
  AnnotationDataList,
  AnnotationDataResponse
} from '@/types/api'

export interface BatchFilterOptions {
  // 包含关键词
  includeKeywords?: string[]
  // 排除关键词
  excludeKeywords?: string[]
  // 包含标签
  includeLabels?: string[]
  // 排除标签
  excludeLabels?: string[]
  // 只显示未标注的
  unlabeledOnly?: boolean
  // 分页
  page?: number
  perPage?: number
}

export interface BatchUpdateOptions {
  // 要添加的标签
  addLabels?: string[]
  // 要删除的标签
  removeLabels?: string[]
}

export class BatchAnnotationService {
  /**
   * 批量筛选文本数据
   * @param options 筛选条件
   * @returns 筛选结果
   */
  async filterTexts(options: BatchFilterOptions): Promise<AnnotationDataList> {
    const searchParams: AdvancedSearchRequest = {
      // query: options.includeKeywords?.join(' ') || undefined,
      // exclude_query: options.excludeKeywords?.join(' ') || undefined,
      keywords: options.includeKeywords || undefined,
      exclude_keywords: options.excludeKeywords || undefined,
      labels: options.includeLabels?.join(',') || undefined,
      exclude_labels: options.excludeLabels?.join(',') || undefined,
      unlabeled_only: options.unlabeledOnly,
      page: options.page || 1,
      per_page: options.perPage || 50
    }

    return await annotationApi.advancedSearch(searchParams)
  }

  /**
   * 通过搜索条件批量更新标签
   * @param filterOptions 筛选条件
   * @param updateOptions 更新选项
   * @returns 更新结果
   */
  async updateLabelsByFilter(
    filterOptions: BatchFilterOptions,
    updateOptions: BatchUpdateOptions
  ): Promise<BulkUpdateLabelsResponse> {
    const searchCriteria: AdvancedSearchRequest = {
      query: filterOptions.includeKeywords?.join(' ') || undefined,
      exclude_query: filterOptions.excludeKeywords?.join(' ') || undefined,
      labels: filterOptions.includeLabels?.join(',') || undefined,
      exclude_labels: filterOptions.excludeLabels?.join(',') || undefined,
      unlabeled_only: filterOptions.unlabeledOnly,
      page: filterOptions.page || 1,
      per_page: filterOptions.perPage || 1000 // 批量操作时增加每页数量
    }

    const request: BulkUpdateLabelsRequest = {
      search_criteria: searchCriteria,
      labels_to_add: updateOptions.addLabels?.join(',') || undefined,
      labels_to_remove: updateOptions.removeLabels?.join(',') || undefined
    }

    return await annotationApi.bulkUpdateLabels(request)
  }

  /**
   * 通过ID列表批量更新标签
   * @param textIds 文本ID列表
   * @param updateOptions 更新选项
   * @returns 更新结果
   */
  async updateLabelsByIds(
    textIds: number[],
    updateOptions: BatchUpdateOptions
  ): Promise<BulkUpdateLabelsResponse> {
    const request: BulkUpdateLabelsRequest = {
      text_ids: textIds,
      labels_to_add: updateOptions.addLabels?.join(',') || undefined,
      labels_to_remove: updateOptions.removeLabels?.join(',') || undefined
    }

    return await annotationApi.bulkUpdateLabels(request)
  }

  /**
   * 为筛选的文本批量添加标签
   * @param filterOptions 筛选条件
   * @param labels 要添加的标签
   * @returns 更新结果
   */
  async addLabelsToFiltered(
    filterOptions: BatchFilterOptions,
    labels: string[]
  ): Promise<BulkUpdateLabelsResponse> {
    return await this.updateLabelsByFilter(filterOptions, { addLabels: labels })
  }

  /**
   * 为筛选的文本批量删除标签
   * @param filterOptions 筛选条件
   * @param labels 要删除的标签
   * @returns 更新结果
   */
  async removeLabelsFromFiltered(
    filterOptions: BatchFilterOptions,
    labels: string[]
  ): Promise<BulkUpdateLabelsResponse> {
    return await this.updateLabelsByFilter(filterOptions, { removeLabels: labels })
  }

  /**
   * 为指定ID的文本批量添加标签
   * @param textIds 文本ID列表
   * @param labels 要添加的标签
   * @returns 更新结果
   */
  async addLabelsToTexts(textIds: number[], labels: string[]): Promise<BulkUpdateLabelsResponse> {
    return await this.updateLabelsByIds(textIds, { addLabels: labels })
  }

  /**
   * 为指定ID的文本批量删除标签
   * @param textIds 文本ID列表
   * @param labels 要删除的标签
   * @returns 更新结果
   */
  async removeLabelsFromTexts(textIds: number[], labels: string[]): Promise<BulkUpdateLabelsResponse> {
    return await this.updateLabelsByIds(textIds, { removeLabels: labels })
  }

  /**
   * 预览筛选结果（不执行更新）
   * @param filterOptions 筛选条件
   * @returns 将被影响的文本列表
   */
  async previewFilter(filterOptions: BatchFilterOptions): Promise<{
    texts: AnnotationDataResponse[]
    totalCount: number
  }> {
    const result = await this.filterTexts({
      ...filterOptions,
      page: 1,
      perPage: 100 // 预览时限制数量
    })

    return {
      texts: result.items,
      totalCount: result.total
    }
  }
}

// 导出单例实例
export const batchAnnotationService = new BatchAnnotationService()

// 导出便利方法
export const batchApi = {
  // 筛选相关
  filter: (options: BatchFilterOptions) => batchAnnotationService.filterTexts(options),
  preview: (options: BatchFilterOptions) => batchAnnotationService.previewFilter(options),
  
  // 批量更新相关
  updateByFilter: (filterOptions: BatchFilterOptions, updateOptions: BatchUpdateOptions) =>
    batchAnnotationService.updateLabelsByFilter(filterOptions, updateOptions),
  updateByIds: (textIds: number[], updateOptions: BatchUpdateOptions) =>
    batchAnnotationService.updateLabelsByIds(textIds, updateOptions),
  
  // 便利方法
  addLabels: (filterOptions: BatchFilterOptions, labels: string[]) =>
    batchAnnotationService.addLabelsToFiltered(filterOptions, labels),
  removeLabels: (filterOptions: BatchFilterOptions, labels: string[]) =>
    batchAnnotationService.removeLabelsFromFiltered(filterOptions, labels),
  addLabelsToTexts: (textIds: number[], labels: string[]) =>
    batchAnnotationService.addLabelsToTexts(textIds, labels),
  removeLabelsFromTexts: (textIds: number[], labels: string[]) =>
    batchAnnotationService.removeLabelsFromTexts(textIds, labels)
}

// 重新导出基础API，方便统一导入
export { annotationApi, labelApi, importApi, statsApi, healthApi } from './api' 