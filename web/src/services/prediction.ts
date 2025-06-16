/**
 * 意图预测服务
 * 调用后端的意图识别接口
 */

import axios, { type AxiosResponse, type AxiosInstance } from 'axios'

// 预测请求类型
export interface PredictRequest {
  query: string
}

// 预测响应类型
export interface PredictResponse {
  intent: string
  prob: number
  query: string
  result_dict: Record<string, number>
  status: number
}

class PredictionService {
  private axiosInstance: AxiosInstance

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }

  // 预测意图
  async predict(query: string): Promise<PredictResponse> {
    // 使用本地后端代理，避免跨域问题
    const url = '/prediction/predict'
    
    try {
      const response: AxiosResponse<PredictResponse> = await this.axiosInstance.post(url, {
        query
      })
      
      return response.data
    } catch (error: any) {
      console.error('[Prediction] Error:', error)
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        '预测服务请求失败'
      )
    }
  }

  // 测试连接
  async testConnection(): Promise<boolean> {
    const url = '/prediction/test-connection'
    
    try {
      const response = await this.axiosInstance.post(url, {})
      return response.data.success === true
    } catch {
      return false
    }
  }
}

export const predictionService = new PredictionService()
export default predictionService 