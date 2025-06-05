/**
 * API 请求工具类
 * 提供与后端交互的所有方法
 */

import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import type {
  AnnotationDataCreate,
  AnnotationDataUpdate,
  AnnotationDataResponse,
  AnnotationDataList,
  LabelCreate,
  LabelResponse,
  SearchRequest,
  AdvancedSearchRequest,
  TextImportRequest,
  BulkLabelRequest,
  BulkUpdateLabelsRequest,
  BulkUpdateLabelsResponse,
  ImportRequest,
  ImportStats,
  SystemStats,
  ApiError
} from '@/types/api'

class ApiService {
  private axiosInstance: AxiosInstance

  constructor(baseURL: string = 'http://localhost:8000') {
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data)
        return config
      },
      (error) => {
        console.error('[API] Request error:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`[API] Response ${response.status}:`, response.data)
        return response
      },
      (error) => {
        console.error('[API] Response error:', error.response?.data || error.message)
        return Promise.reject(this.handleError(error))
      }
    )
  }

  private handleError(error: any): ApiError {
    if (error.response?.data) {
      return {
        detail: error.response.data.detail || error.response.data.message || '请求失败',
        status_code: error.response.status
      }
    }
    return {
      detail: error.message || '网络连接失败',
      status_code: 0
    }
  }

  // 标注数据相关方法
  async createAnnotation(data: AnnotationDataCreate): Promise<AnnotationDataResponse> {
    const response = await this.axiosInstance.post<AnnotationDataResponse>('/annotations/', data)
    return response.data
  }

  async getAnnotation(id: number): Promise<AnnotationDataResponse> {
    const response = await this.axiosInstance.get<AnnotationDataResponse>(`/annotations/${id}`)
    return response.data
  }

  async updateAnnotation(id: number, data: AnnotationDataUpdate): Promise<AnnotationDataResponse> {
    const response = await this.axiosInstance.put<AnnotationDataResponse>(`/annotations/${id}`, data)
    return response.data
  }

  async deleteAnnotation(id: number): Promise<void> {
    await this.axiosInstance.delete(`/annotations/${id}`)
  }

  async searchAnnotations(searchParams: SearchRequest): Promise<AnnotationDataList> {
    const response = await this.axiosInstance.post<AnnotationDataList>('/annotations/search', searchParams)
    return response.data
  }

  // 高级搜索（支持排除条件）
  async advancedSearchAnnotations(searchParams: AdvancedSearchRequest): Promise<AnnotationDataList> {
    const response = await this.axiosInstance.post<AnnotationDataList>('/annotations/search', searchParams)
    return response.data
  }

  async bulkLabelAnnotations(data: BulkLabelRequest): Promise<{ updated_count: number }> {
    const response = await this.axiosInstance.post<{ updated_count: number }>('/annotations/bulk-label', data)
    return response.data
  }

  // 批量标签更新（增删标签）
  async bulkUpdateLabels(data: BulkUpdateLabelsRequest): Promise<BulkUpdateLabelsResponse> {
    const response = await this.axiosInstance.post<BulkUpdateLabelsResponse>('/annotations/bulk-update-labels', data)
    return response.data
  }

  async importTexts(data: TextImportRequest): Promise<{ imported_count: number }> {
    const response = await this.axiosInstance.post<{ imported_count: number }>('/annotations/import-texts', data)
    return response.data
  }

  // 标签管理相关方法
  async createLabel(data: LabelCreate): Promise<LabelResponse> {
    const response = await this.axiosInstance.post<LabelResponse>('/labels/', data)
    return response.data
  }

  async getAllLabels(): Promise<LabelResponse[]> {
    const response = await this.axiosInstance.get<LabelResponse[]>('/labels/')
    return response.data
  }

  async getLabel(id: number): Promise<LabelResponse> {
    const response = await this.axiosInstance.get<LabelResponse>(`/labels/${id}`)
    return response.data
  }

  async deleteLabel(id: number): Promise<void> {
    await this.axiosInstance.delete(`/labels/${id}`)
  }

  // 数据导入相关方法
  async importOldData(oldDataPath: string = '../old-data'): Promise<ImportStats> {
    const response = await this.axiosInstance.post<ImportStats>('/import/old-data', null, {
      params: { old_data_path: oldDataPath }
    })
    return response.data
  }

  async importLabelConfig(configPath: string = '../old-data/label_config.yaml'): Promise<{ message: string }> {
    const response = await this.axiosInstance.post<{ message: string }>('/import/label-config', null, {
      params: { config_path: configPath }
    })
    return response.data
  }

  async importTextFile(data: ImportRequest): Promise<ImportStats> {
    const response = await this.axiosInstance.post<ImportStats>('/import/text-file', data)
    return response.data
  }

  // 统计相关方法
  async getSystemStats(): Promise<SystemStats> {
    const response = await this.axiosInstance.get<SystemStats>('/stats/system')
    return response.data
  }

  async getStats(): Promise<SystemStats> {
    const response = await this.axiosInstance.get<SystemStats>('/stats')
    return response.data
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.axiosInstance.get<{ status: string }>('/health')
    return response.data
  }
}

// 创建单例实例
export const apiService = new ApiService()

// 导出常用方法（扁平化API）
export const annotationApi = {
  create: (data: AnnotationDataCreate) => apiService.createAnnotation(data),
  get: (id: number) => apiService.getAnnotation(id),
  update: (id: number, data: AnnotationDataUpdate) => apiService.updateAnnotation(id, data),
  delete: (id: number) => apiService.deleteAnnotation(id),
  search: (params: SearchRequest) => apiService.searchAnnotations(params),
  advancedSearch: (params: AdvancedSearchRequest) => apiService.advancedSearchAnnotations(params),
  bulkLabel: (data: BulkLabelRequest) => apiService.bulkLabelAnnotations(data),
  bulkUpdateLabels: (data: BulkUpdateLabelsRequest) => apiService.bulkUpdateLabels(data),
  importTexts: (data: TextImportRequest) => apiService.importTexts(data)
}

export const labelApi = {
  create: (data: LabelCreate) => apiService.createLabel(data),
  getAll: () => apiService.getAllLabels(),
  get: (id: number) => apiService.getLabel(id),
  delete: (id: number) => apiService.deleteLabel(id)
}

export const importApi = {
  oldData: (path?: string) => apiService.importOldData(path),
  labelConfig: (path?: string) => apiService.importLabelConfig(path),
  textFile: (data: ImportRequest) => apiService.importTextFile(data)
}

export const statsApi = {
  system: () => apiService.getSystemStats(),
  get: () => apiService.getStats()
}

export const healthApi = {
  check: () => apiService.healthCheck()
} 