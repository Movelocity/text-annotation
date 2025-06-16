<script setup lang="ts">
import { ref } from 'vue'
import { ElCard, ElInput, ElButton, ElMessage, ElAlert, ElTag } from 'element-plus'
import { predictionService, type PredictResponse } from '@/services/prediction'

// 响应式状态
const query = ref('')
const isLoading = ref(false)
const result = ref<PredictResponse | null>(null)
const error = ref('')

// 预测意图
const predictIntent = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('请输入查询文本')
    return
  }

  isLoading.value = true
  error.value = ''
  result.value = null

  try {
    const response = await predictionService.predict(query.value.trim())
    result.value = response
    ElMessage.success('预测完成')
  } catch (err: any) {
    error.value = err.message
    ElMessage.error(`预测失败: ${err.message}`)
  } finally {
    isLoading.value = false
  }
}

// 清空结果
const clearResult = () => {
  query.value = ''
  result.value = null
  error.value = ''
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

<template>
  <div class="prediction-test">
    <ElCard>
      <template #header>
        <div class="card-header">
          <span>意图预测测试</span>
          <ElButton 
            v-if="result || error" 
            size="small" 
            @click="clearResult"
          >
            清空
          </ElButton>
        </div>
      </template>

      <div class="test-content">
        <!-- 输入区域 -->
        <div class="input-section">
          <ElInput
            v-model="query"
            type="textarea"
            :rows="3"
            placeholder="请输入要预测意图的文本..."
            :disabled="isLoading"
            @keyup.ctrl.enter="predictIntent"
          />
          <div class="input-actions">
            <ElButton 
              type="primary" 
              @click="predictIntent"
              :loading="isLoading"
              :disabled="!query.trim()"
            >
              {{ isLoading ? '预测中...' : '预测意图' }}
            </ElButton>
          </div>
          <div class="input-tip">
            提示：按 Ctrl + Enter 快速预测
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="error" class="error-section">
          <ElAlert
            :title="error"
            type="error"
            show-icon
            :closable="false"
          />
        </div>

        <!-- 预测结果 -->
        <div v-if="result" class="result-section">
          <ElAlert
            title="预测结果"
            type="success"
            show-icon
            :closable="false"
          >
            <div class="result-content">
              <!-- 主要意图 -->
              <div class="main-result">
                <div class="intent-name">
                  <strong>预测意图:</strong> 
                  <ElTag size="large" :type="getConfidenceType(result.prob)">
                    {{ result.intent }}
                  </ElTag>
                </div>
                <div class="confidence">
                  <strong>置信度:</strong> 
                  <ElTag size="large" :type="getConfidenceType(result.prob)">
                    {{ formatProbability(result.prob) }}
                  </ElTag>
                </div>
              </div>

              <!-- 详细结果 -->
              <div class="detailed-results">
                <div class="result-title">所有意图得分:</div>
                <div class="scores-list">
                  <div 
                    v-for="(score, intent) in result.result_dict" 
                    :key="intent"
                    class="score-item"
                  >
                    <span class="intent-label">{{ intent }}:</span>
                    <ElTag :type="getConfidenceType(score)">
                      {{ formatProbability(score) }}
                    </ElTag>
                  </div>
                </div>
              </div>

              <!-- 原始查询 -->
              <div class="query-display">
                <div class="query-title">原始查询:</div>
                <div class="query-text">{{ result.query }}</div>
              </div>
            </div>
          </ElAlert>
        </div>
      </div>
    </ElCard>
  </div>
</template>

<style scoped>
.prediction-test {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.input-tip {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: right;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.main-result {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
  flex-wrap: wrap;
}

.intent-name,
.confidence {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.detailed-results {
  background-color: var(--background-dark);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.result-title {
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.scores-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xs) 0;
}

.intent-label {
  font-family: monospace;
  color: var(--text-primary);
}

.query-display {
  background-color: var(--background-dark);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.query-title {
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.query-text {
  font-style: italic;
  color: var(--text-secondary);
  line-height: 1.5;
}

.error-section {
  margin-top: var(--spacing-md);
}
</style> 