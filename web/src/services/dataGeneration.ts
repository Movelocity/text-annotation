/**
 * 数据生成服务
 * 处理AI生成、手动创建和文件导入的相关API调用
 */

import { generateApi, annotationApi } from './api'
import type { AnnotationDataCreate } from '@/types/api'

// 从API服务导入相关接口
export interface GenerateRequest {
  api_key: string
  base_url: string
  model: string
  system_prompt: string
  user_prompt: string
  count: number
  temperature?: number
  max_tokens?: number
}

export interface GeneratedText {
  text: string
  labels?: string
  raw_output: string
}

export interface GenerateStatus {
  status: string
  progress: number
  current_count: number
  total_count: number
  message?: string
  error?: string
}

// 数据生成配置接口
export interface GenerationConfig {
  apiKey: string
  baseUrl: string
  model: string
  systemPrompt: string
  userPrompt: string
  count: number
  temperature: number
}

/**
 * 数据生成服务类
 */
export class DataGenerationService {
  
  /**
   * 启动AI数据生成任务
   */
  async startGeneration(config: GenerationConfig) {
    const request: GenerateRequest = {
      api_key: config.apiKey,
      base_url: config.baseUrl,
      model: config.model,
      system_prompt: config.systemPrompt,
      user_prompt: config.userPrompt,
      count: config.count,
      temperature: config.temperature
    }
    
    return generateApi.start(request)
  }
  
  /**
   * 获取生成任务状态
   */
  async getGenerationStatus(taskId: string) {
    return generateApi.getStatus(taskId)
  }
  
  /**
   * 获取生成结果
   */
  async getGenerationResults(taskId: string) {
    return generateApi.getResults(taskId)
  }
  
  /**
   * 取消生成任务
   */
  async cancelGeneration(taskId: string) {
    return generateApi.cancel(taskId)
  }
  
  /**
   * 创建流式连接监听生成进度
   */
  createGenerationStream(taskId: string): EventSource {
    return generateApi.createEventSource(taskId)
  }
  
  /**
   * 手动创建单条标注数据
   */
  async createAnnotation(data: AnnotationDataCreate) {
    return annotationApi.create(data)
  }
  
  /**
   * 批量导入文本数据
   */
  async importTexts(texts: string[]) {
    return annotationApi.importTexts({ texts })
  }
  
  /**
   * 保存配置到 localStorage
   */
  saveConfig(config: GenerationConfig): void {
    const configToSave = {
      apiKey: config.apiKey,
      baseUrl: config.baseUrl,
      model: config.model,
      systemPrompt: config.systemPrompt,
      userPrompt: config.userPrompt,
      temperature: config.temperature
    }
    localStorage.setItem('data-import-config', JSON.stringify(configToSave))
  }
  
  /**
   * 从 localStorage 加载配置
   */
  loadConfig(): Partial<GenerationConfig> {
    try {
      const savedConfig = localStorage.getItem('data-import-config')
      if (savedConfig) {
        return JSON.parse(savedConfig)
      }
    } catch (error) {
      console.error('加载配置失败:', error)
    }
    return {}
  }
}

// 导出服务实例
export const dataGenerationService = new DataGenerationService() 