/**
 * API 相关的 TypeScript 类型定义
 * 基于后端 Pydantic schemas
 */

// 标注数据相关类型
export interface AnnotationDataBase {
  text: string
  labels?: string | null
}

export interface AnnotationDataCreate extends AnnotationDataBase {}

export interface AnnotationDataUpdate {
  labels?: string | null
}

export interface AnnotationDataResponse extends AnnotationDataBase {
  id: number
}

export interface AnnotationDataList {
  items: AnnotationDataResponse[]
  total: number
  page: number
  per_page: number
}

// 标签相关类型
export interface LabelBase {
  label: string
}

export interface LabelCreate extends LabelBase {
  id?: number | null
}

export interface LabelResponse extends LabelBase {
  id: number
}

// 导入相关类型
export interface ImportStats {
  files_processed: number
  records_imported: number
  duplicates_merged: number
}

export interface ImportRequest {
  file_path: string
}

export interface TextImportRequest {
  texts: string[]
}

export interface BulkLabelRequest {
  text_ids: number[]
  labels: string
}

// 搜索相关类型
export interface SearchRequest {
  query?: string | null
  labels?: string | null
  unlabeled_only?: boolean
  page?: number
  per_page?: number
}

// 统计相关类型
export interface LabelStats {
  label: string
  count: number
}

export interface SystemStats {
  total_texts: number
  labeled_texts: number
  unlabeled_texts: number
  total_labels: number
  label_statistics: LabelStats[]
}

// 通用API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
}

// API错误类型
export interface ApiError {
  detail: string
  status_code?: number
} 