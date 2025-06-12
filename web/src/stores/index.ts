/**
 * Pinia stores 主配置文件
 */

import { createPinia } from 'pinia'

export const pinia = createPinia()

// 导出所有store
export * from './annotation'
export * from './label'
export * from './app' 