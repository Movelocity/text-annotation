/**
 * 标签处理工具函数
 */

/**
 * 解析标签字符串为数组
 * @param labels - 标签字符串（逗号分隔）或null
 * @returns 标签数组
 */
export function parseLabels(labels: string | null | undefined): string[] {
  if (!labels || typeof labels !== 'string') {
    return []
  }
  
  return labels
    .split(',')
    .map(label => label.trim())
    .filter(label => label.length > 0)
}

/**
 * 将标签数组转换为字符串
 * @param labels - 标签数组
 * @returns 逗号分隔的标签字符串
 */
export function stringifyLabels(labels: string[]): string {
  return labels.filter(label => label.trim().length > 0).join(',')
} 