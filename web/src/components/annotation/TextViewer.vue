<!--
  文本查看器组件
  功能：显示当前选中的文本内容和基本信息
-->
<template>
  <div class="text-viewer">
    <div class="viewer-header">
      <h3>文本内容</h3>
      <div class="text-info" v-if="currentItem">
        <el-tag size="small" type="info">ID: {{ currentItem.id }}</el-tag>
        <el-tag size="small">{{ currentItem.text.length }} 字符</el-tag>
      </div>
    </div>

    <div v-if="!currentItem" class="no-selection">
      <el-empty description="请从左侧列表选择要标注的文本" />
    </div>

    <div v-else class="viewer-content">
      <!-- 文本内容 -->
      <div class="text-content">
        <div class="text-display">
          {{ currentItem.text }}
        </div>
      </div>

      <!-- 当前标签状态 -->
      <div class="label-status">
        <div class="status-title">当前标签</div>
        <div class="status-content">
          <template v-if="currentLabels.length > 0">
            <el-tag
              v-for="label in currentLabels"
              :key="label"
              type="success"
              size="large"
              style="font-size: 14px; font-weight: bold;"
              class="label-tag"
            >
              {{ label }}
            </el-tag>
          </template>
          <span v-else class="no-label">未标注</span>
        </div>
      </div>

      <!-- 意图预测区域 -->
      <div class="prediction-section">

        <!-- 加载中状态 -->
        <div v-if="isLoading" class="prediction-loading">
          <div class="loading-content">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span class="loading-text">正在分析文本意图...</span>
          </div>
        </div>

        <!-- 预测结果 -->
        <div v-else-if="predictionResult" class="prediction-result">
          <div class="main-prediction">
            <div class="prediction-result-header">
              <span class="prediction-label">预测意图：</span>
              <el-tag 
                :type="getConfidenceType(predictionResult.prob)" 
                size="large"
              >
                {{ predictionResult.intent }}
              </el-tag>
              <span class="confidence">
                ({{ formatProbability(predictionResult.prob) }})
              </span>
            </div>
            <ModernButton
              text="重新预测"
              icon="fas fa-redo"
              :disabled="!currentItem?.text.trim()"
              @click="predictIntent"
            />
          </div>
          
          <!-- 详细得分 -->
          <div class="scores-detail">
            <div 
              v-for="(score, intent) in predictionResult.result_dict" 
              :key="intent"
              class="score-item"
            >
              <span class="intent-name">{{ intent }}</span>
              <el-tag :type="getConfidenceType(score)" size="small">
                {{ formatProbability(score) }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="predictionError" class="prediction-error">
          <el-alert
            :title="predictionError"
            type="error"
            size="small"
            show-icon
            :closable="false"
          />
          <div class="error-actions">
            <ModernButton
              text="重试"
              icon="fas fa-redo"
              :disabled="!currentItem?.text.trim()"
              @click="predictIntent"
            />
          </div>
        </div>

        <!-- 初始状态 -->
        <div v-else class="prediction-initial flex-row justify-between">
          <div class="initial-content flex-row justify-center">
            <el-icon class="prediction-icon"><MagicStick /></el-icon>
            <span class="tip">点击按钮分析当前文本的意图</span>
            
          </div>
          <ModernButton
              text="预测意图"
              icon="fas fa-rocket"
              :disabled="!currentItem?.text.trim()"
              @click="predictIntent"
            />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, MagicStick } from '@element-plus/icons-vue'
import type { AnnotationDataResponse } from '@/types/api'
import { predictionService, type PredictResponse } from '@/services/prediction'
import ModernButton from '@/components/common/ModernButton.vue'

// Props
interface Props {
  currentItem?: AnnotationDataResponse | null
}

const props = defineProps<Props>()

// 预测相关状态
const isLoading = ref(false)
const predictionResult = ref<PredictResponse | null>(null)
const predictionError = ref('')

// 监听 currentItem 变化，重置预测状态
watch(() => props.currentItem, () => {
  // 重置预测相关状态
  predictionResult.value = null
  predictionError.value = ''
  isLoading.value = false
})

// 计算属性
const currentLabels = computed(() => {
  if (!props.currentItem?.labels) return []
  return props.currentItem.labels.split(',').map(label => label.trim()).filter(label => label)
})

// 预测意图
const predictIntent = async () => {
  if (!props.currentItem?.text.trim()) {
    ElMessage.warning('没有可预测的文本内容')
    return
  }

  isLoading.value = true
  predictionError.value = ''
  predictionResult.value = null

  try {
    const response = await predictionService.predict(props.currentItem.text.trim())
    predictionResult.value = response
    ElMessage.success('预测完成')
  } catch (err: any) {
    predictionError.value = err.message
    ElMessage.error(`预测失败: ${err.message}`)
  } finally {
    isLoading.value = false
  }
}

// 获取置信度标签类型
const getConfidenceType = (prob: number) => {
  if (prob >= 0.8) return 'success'
  if (prob >= 0.6) return 'warning'
  return 'danger'
}

// 格式化概率为百分比
const formatProbability = (prob: number) => {
  return (prob * 100).toFixed(2) + '%'
}
</script>

<style scoped>
.text-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.viewer-header h3 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.text-info {
  display: flex;
  gap: 8px;
}

.no-selection {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.text-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.text-display {
  flex: 1;
  padding: 16px;
  background: var(--el-bg-color-page);
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  font-size: 16px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
  word-break: break-word;
  overflow-y: auto;
  max-height: 400px;
}

.label-status {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-title,
.section-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  font-size: 14px;
}

.status-content {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
}

.label-tag {
  margin: 2px 0;
}

.no-label {
  color: var(--el-text-color-secondary);
  font-style: italic;
}

/* 预测区域样式 */
.prediction-section {
  flex-shrink: 0;
}

.prediction-result {
  padding: 12px;
  /* background: var(--el-bg-color-page); */
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
}

.main-prediction {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}

.prediction-result-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.prediction-label {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.confidence {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.scores-detail {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.intent-name {
  font-size: 14px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.prediction-error {
  margin-top: 8px;
}

/* 移除不再使用的 .no-prediction 样式 */

.tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  font-style: italic;
}

.prediction-loading {
  padding: 20px;
  text-align: center;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-text {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  font-style: italic;
}

.prediction-initial {
  padding: 20px;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
}

.initial-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
}

.prediction-icon {
  font-size: 24px;
  color: var(--el-text-color-secondary);
}

.scores-header {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  font-size: 14px;
}

.error-actions {
  margin-top: 8px;
  display: flex;
  justify-content: center;
}
</style> 