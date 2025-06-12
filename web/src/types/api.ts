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
  description?: string | null
  groups?: string | null
}

export interface LabelCreate extends LabelBase {
  id?: number | null
}

export interface LabelUpdate extends LabelBase {}

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

// 高级搜索相关类型（增强版）
export interface AdvancedSearchRequest {
  query?: string | null              // 必须包含的关键词（模糊搜索、正则搜索，暂不开发）
  exclude_query?: string | null      // 不能包含的关键词（模糊搜索、正则搜索，暂不开发）
  keywords?: string[] | null         // 必须包含的关键词数组（精确包含搜索）
  exclude_keywords?: string[] | null // 不能包含的关键词数组（精确包含搜索）
  labels?: string | null             // 必须包含的标签（逗号分隔）
  exclude_labels?: string | null     // 不能包含的标签（逗号分隔）
  unlabeled_only?: boolean
  page?: number
  per_page?: number
}

// 批量标签更新相关类型
export interface BulkUpdateLabelsRequest {
  // 方式1：通过搜索条件筛选
  search_criteria?: AdvancedSearchRequest
  // 方式2：通过ID列表
  text_ids?: number[]
  // 要添加的标签
  labels_to_add?: string | null
  // 要删除的标签
  labels_to_remove?: string | null
}

export interface BulkUpdateLabelsResponse {
  updated_count: number
  message: string
}

// 搜索相关类型（保持向后兼容）
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