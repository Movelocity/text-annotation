<template>
  <div class="data-import-page">
    <div class="page-header">
      <h1>数据导入</h1>
      <p class="description">支持单条数据导入、批量文件导入和AI数据生成</p>
    </div>

    <el-tabs v-model="activeTab" class="import-tabs">
      <!-- 单条数据导入 -->
      <el-tab-pane label="单条导入" name="single">
        <div class="tab-content">
          <h3>单条数据导入</h3>
          <p class="tab-description">手动输入单条文本数据进行导入</p>
          
          <el-form 
            ref="singleFormRef" 
            :model="singleForm" 
            :rules="singleFormRules"
            label-width="120px"
            class="single-import-form"
          >
            <el-form-item label="文本内容" prop="text">
              <el-input
                v-model="singleForm.text"
                type="textarea"
                :rows="6"
                placeholder="请输入要导入的文本内容"
                show-word-limit
                maxlength="5000"
              />
            </el-form-item>
            
            <el-form-item label="标签" prop="labels">
              <el-input
                v-model="singleForm.labels"
                placeholder="请输入标签，多个标签用逗号分隔，例如：客服,投诉"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleSingleImport"
                :loading="singleLoading"
              >
                导入数据
              </el-button>
              <el-button @click="resetSingleForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 批量数据导入 -->
      <el-tab-pane label="批量导入" name="batch">
        <div class="tab-content">
          <h3>批量数据导入</h3>
          <p class="tab-description">上传文件进行批量数据导入，支持 .txt 和 .csv 格式</p>
          
          <div class="batch-import-section">
            <!-- 文件上传区域 -->
            <div class="upload-section">
              <el-upload
                ref="uploadRef"
                class="upload-demo"
                drag
                :auto-upload="false"
                :on-change="handleFileChange"
                :before-upload="beforeFileUpload"
                accept=".txt,.csv"
                :limit="1"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 .txt 和 .csv 格式，文件大小不超过10MB
                  </div>
                </template>
              </el-upload>
            </div>

            <!-- 数据预览区域 -->
            <div v-if="batchData.length > 0" class="preview-section">
              <div class="preview-header">
                <h4>数据预览 ({{batchData.length}} 条)</h4>
                <div class="preview-actions">
                  <el-button size="small" @click="selectAll">全选</el-button>
                  <el-button size="small" @click="selectNone">取消全选</el-button>
                  <el-button 
                    type="primary" 
                    size="small"
                    @click="handleBatchImport"
                    :loading="batchLoading"
                    :disabled="selectedRows.length === 0"
                  >
                    导入选中 ({{selectedRows.length}})
                  </el-button>
                </div>
              </div>
              
              <el-table
                ref="batchTableRef"
                :data="batchData"
                @selection-change="handleSelectionChange"
                max-height="400"
                stripe
              >
                <el-table-column type="selection" width="55" />
                <el-table-column prop="index" label="序号" width="80" />
                <el-table-column prop="text" label="文本内容" min-width="300" show-overflow-tooltip />
                <el-table-column prop="labels" label="标签" width="200" show-overflow-tooltip />
              </el-table>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 数据生成 -->
      <el-tab-pane label="数据生成" name="generate">
        <div class="tab-content">
          <h3>AI数据生成</h3>
          <p class="tab-description">使用大模型API生成标注数据</p>
          
          <div class="generate-section">
            <!-- API配置 -->
            <el-card class="config-card" header="API配置">
              <el-form :model="generateConfig" label-width="120px">
                <el-form-item label="API Key">
                  <el-input
                    v-model="generateConfig.apiKey"
                    placeholder="请输入API Key"
                    show-password
                    @blur="saveConfig"
                  />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input
                    v-model="generateConfig.baseUrl"
                    placeholder="例如：https://api.openai.com/v1"
                    @blur="saveConfig"
                  />
                </el-form-item>
                <el-form-item label="模型名称">
                  <el-input
                    v-model="generateConfig.model"
                    placeholder="例如：gpt-3.5-turbo"
                    @blur="saveConfig"
                  />
                </el-form-item>
              </el-form>
            </el-card>

            <!-- 提示词模板 -->
            <el-card class="config-card" header="提示词模板">
              <el-form :model="generateConfig" label-width="120px">
                <el-form-item label="系统提示词">
                  <el-input
                    v-model="generateConfig.systemPrompt"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入系统提示词"
                    @blur="saveConfig"
                  />
                </el-form-item>
                <el-form-item label="用户提示词">
                  <el-input
                    v-model="generateConfig.userPrompt"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入用户提示词"
                    @blur="saveConfig"
                  />
                </el-form-item>
              </el-form>
            </el-card>

            <!-- 解析配置 -->
            <el-card class="config-card" header="数据解析">
              <el-form :model="generateConfig" label-width="120px">
                <el-form-item label="解析正则">
                  <el-input
                    v-model="generateConfig.parseRegex"
                    placeholder="用于提取生成文本中的有效数据"
                    @blur="saveConfig"
                  />
                </el-form-item>
                <el-form-item label="生成数量">
                  <el-input-number
                    v-model="generateConfig.count"
                    :min="1"
                    :max="100"
                    @change="saveConfig"
                  />
                </el-form-item>
              </el-form>
            </el-card>

            <!-- 生成控制 -->
            <div class="generate-controls">
              <el-button 
                type="primary" 
                @click="handleGenerate"
                :loading="generateLoading"
                :disabled="!isConfigValid"
              >
                开始生成
              </el-button>
              <el-button 
                v-if="generateLoading" 
                @click="handleCancelGenerate"
              >
                取消生成
              </el-button>
            </div>

            <!-- 生成结果 -->
            <div v-if="generatedData.length > 0" class="generated-results">
              <h4>生成结果 ({{generatedData.length}} 条)</h4>
              <el-table :data="generatedData" max-height="300" stripe>
                <el-table-column prop="text" label="生成文本" min-width="300" show-overflow-tooltip />
                <el-table-column prop="labels" label="标签" width="200" show-overflow-tooltip />
                <el-table-column prop="raw_output" label="原始输出" width="150" show-overflow-tooltip />
                <el-table-column label="操作" width="100">
                  <template #default="scope">
                    <el-button size="small" type="danger" @click="removeGenerated(scope.$index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <div class="generated-actions">
                <el-button 
                  type="primary" 
                  @click="importGeneratedData"
                  :loading="importGeneratedLoading"
                >
                  导入全部生成数据
                </el-button>
                <el-button @click="clearGenerated">清空</el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { FormInstance, UploadInstance, UploadRawFile, UploadUserFile } from 'element-plus'
import { annotationApi, generateApi } from '@/services/api'
import type { AnnotationDataCreate } from '@/types/api'
import type { GenerateRequest, GeneratedText, GenerateStatus } from '@/services/api'

// Tab控制
const activeTab = ref('single')

// ==================== 单条导入 ====================
const singleFormRef = ref<FormInstance>()
const singleLoading = ref(false)

const singleForm = reactive({
  text: '',
  labels: ''
})

const singleFormRules = {
  text: [
    { required: true, message: '请输入文本内容', trigger: 'blur' },
    { min: 1, max: 5000, message: '文本长度应在 1 到 5000 个字符之间', trigger: 'blur' }
  ]
}

const handleSingleImport = async () => {
  if (!singleFormRef.value) return
  
  const valid = await singleFormRef.value.validate()
  if (!valid) return

  singleLoading.value = true
  try {
    const data: AnnotationDataCreate = {
      text: singleForm.text.trim(),
      labels: singleForm.labels.trim() || undefined
    }
    
    await annotationApi.create(data)
    ElMessage.success('数据导入成功！')
    resetSingleForm()
  } catch (error: any) {
    ElMessage.error(error.detail || '导入失败')
  } finally {
    singleLoading.value = false
  }
}

const resetSingleForm = () => {
  if (singleFormRef.value) {
    singleFormRef.value.resetFields()
  }
}

// ==================== 批量导入 ====================
const uploadRef = ref<UploadInstance>()
const batchTableRef = ref()
const batchLoading = ref(false)
const batchData = ref<Array<{ index: number; text: string; labels: string }>>([])
const selectedRows = ref<Array<{ index: number; text: string; labels: string }>>([])

const handleFileChange = (file: UploadUserFile) => {
  const rawFile = file.raw
  if (!rawFile) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target?.result as string
    parseFileContent(content, rawFile.name)
  }
  reader.readAsText(rawFile, 'utf-8')
}

const beforeFileUpload = (file: UploadRawFile) => {
  const isValidType = file.type === 'text/plain' || file.name.endsWith('.txt') || file.name.endsWith('.csv')
  const isValidSize = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只支持 .txt 和 .csv 格式的文件！')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('文件大小不能超过 10MB！')
    return false
  }
  return false // 阻止自动上传
}

const parseFileContent = (content: string, fileName: string) => {
  const lines = content.split('\n').filter(line => line.trim())
  const data = lines.map((line, index) => ({
    index: index + 1,
    text: line.trim(),
    labels: '' // 批量导入时标签为空，用户可以后续标注
  }))
  
  batchData.value = data
  selectedRows.value = [...data] // 默认全选
  
  // 设置表格全选状态
  if (batchTableRef.value) {
    batchTableRef.value.toggleAllSelection()
  }
  
  ElMessage.success(`解析完成，共 ${data.length} 条数据`)
}

const handleSelectionChange = (selection: Array<{ index: number; text: string; labels: string }>) => {
  selectedRows.value = selection
}

const selectAll = () => {
  if (batchTableRef.value) {
    batchTableRef.value.toggleAllSelection()
  }
}

const selectNone = () => {
  if (batchTableRef.value) {
    batchTableRef.value.clearSelection()
  }
}

const handleBatchImport = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要导入的数据')
    return
  }

  const result = await ElMessageBox.confirm(
    `确定要导入选中的 ${selectedRows.value.length} 条数据吗？`,
    '确认导入',
    { type: 'warning' }
  )

  if (result !== 'confirm') return

  batchLoading.value = true
  try {
    const texts = selectedRows.value.map(row => row.text)
    await annotationApi.importTexts({ texts })
    
    ElMessage.success(`成功导入 ${texts.length} 条数据！`)
    
    // 清空数据
    batchData.value = []
    selectedRows.value = []
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
  } catch (error: any) {
    ElMessage.error(error.detail || '批量导入失败')
  } finally {
    batchLoading.value = false
  }
}

// ==================== 数据生成 ====================
const generateLoading = ref(false)
const importGeneratedLoading = ref(false)
const generatedData = ref<Array<GeneratedText>>([])
const currentTaskId = ref<string>('')
const eventSource = ref<EventSource | null>(null)

const generateConfig = reactive({
  apiKey: '',
  baseUrl: '',
  model: 'gpt-3.5-turbo',
  systemPrompt: '你是一个专业的文本数据生成助手，请根据用户要求生成高质量的文本数据。',
  userPrompt: '请生成10条用于意图识别的客服对话文本，每条文本应该包含明确的用户意图。',
  parseRegex: '',
  count: 10,
  temperature: 0.7,
  maxTokens: undefined as number | undefined
})

const isConfigValid = computed(() => {
  return generateConfig.apiKey && generateConfig.baseUrl && generateConfig.model
})

// 加载配置
const loadConfig = () => {
  const saved = localStorage.getItem('data-import-config')
  if (saved) {
    try {
      const config = JSON.parse(saved)
      Object.assign(generateConfig, config)
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }
}

// 保存配置
const saveConfig = () => {
  localStorage.setItem('data-import-config', JSON.stringify(generateConfig))
}

const handleGenerate = async () => {
  if (!isConfigValid.value) {
    ElMessage.warning('请先完善API配置')
    return
  }

  generateLoading.value = true
  generatedData.value = []
  
  try {
    // 创建生成请求
    const request: GenerateRequest = {
      api_key: generateConfig.apiKey,
      base_url: generateConfig.baseUrl,
      model: generateConfig.model,
      system_prompt: generateConfig.systemPrompt,
      user_prompt: generateConfig.userPrompt,
      count: generateConfig.count,
      parse_regex: generateConfig.parseRegex || undefined,
      temperature: generateConfig.temperature,
      max_tokens: generateConfig.maxTokens
    }
    
    // 启动生成任务
    const response = await generateApi.start(request)
    currentTaskId.value = response.task_id
    
    ElMessage.success('生成任务已启动')
    
    // 建立SSE连接获取实时更新
    setupEventSource(response.task_id)
    
  } catch (error: any) {
    ElMessage.error(error.detail || '启动生成任务失败')
    generateLoading.value = false
  }
}

const setupEventSource = (taskId: string) => {
  // 关闭之前的连接
  if (eventSource.value) {
    eventSource.value.close()
  }
  
  eventSource.value = generateApi.createEventSource(taskId)
  
  eventSource.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.error) {
        ElMessage.error(data.error)
        generateLoading.value = false
        return
      }
      
      // 更新状态
      if (data.status === 'generating' && data.latest_text) {
        // 添加新生成的文本
        generatedData.value.push(data.latest_text)
      } else if (data.status === 'completed') {
        ElMessage.success(`生成完成！共生成 ${data.current_count} 条数据`)
        generateLoading.value = false
        eventSource.value?.close()
      } else if (data.status === 'cancelled') {
        ElMessage.info('生成已取消')
        generateLoading.value = false
        eventSource.value?.close()
      } else if (data.status === 'error') {
        ElMessage.error(data.error || '生成过程中出错')
        generateLoading.value = false
        eventSource.value?.close()
      }
      
    } catch (error) {
      console.error('解析SSE数据失败:', error)
    }
  }
  
  eventSource.value.onerror = (error) => {
    console.error('SSE连接错误:', error)
    ElMessage.error('生成连接中断')
    generateLoading.value = false
    eventSource.value?.close()
  }
}

const handleCancelGenerate = async () => {
  if (!currentTaskId.value) {
    return
  }
  
  try {
    await generateApi.cancel(currentTaskId.value)
    generateLoading.value = false
    eventSource.value?.close()
    ElMessage.info('已取消生成')
  } catch (error: any) {
    ElMessage.error(error.detail || '取消生成失败')
  }
}

const removeGenerated = (index: number) => {
  generatedData.value.splice(index, 1)
}

const clearGenerated = () => {
  generatedData.value = []
}

const importGeneratedData = async () => {
  if (generatedData.value.length === 0) {
    ElMessage.warning('没有可导入的生成数据')
    return
  }

  const result = await ElMessageBox.confirm(
    `确定要导入 ${generatedData.value.length} 条生成数据吗？`,
    '确认导入',
    { type: 'warning' }
  )

  if (result !== 'confirm') return

  importGeneratedLoading.value = true
  let successCount = 0
  
  try {
    // 逐条导入生成的数据
    for (const item of generatedData.value) {
      try {
        await annotationApi.create({
          text: item.text,
          labels: item.labels || undefined
        })
        successCount++
      } catch (error) {
        console.error('导入单条数据失败:', error)
        // 继续导入其他数据
      }
    }
    
    if (successCount === generatedData.value.length) {
      ElMessage.success(`成功导入 ${successCount} 条生成数据！`)
    } else {
      ElMessage.warning(`成功导入 ${successCount}/${generatedData.value.length} 条数据`)
    }
    
    clearGenerated()
  } catch (error: any) {
    ElMessage.error(error.detail || '导入生成数据失败')
  } finally {
    importGeneratedLoading.value = false
  }
}

// 组件挂载时加载配置
onMounted(() => {
  loadConfig()
})

// 组件卸载时清理资源
onUnmounted(() => {
  if (eventSource.value) {
    eventSource.value.close()
  }
})
</script>

<style scoped>
.data-import-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.import-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 20px 0;
}

.tab-content h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.tab-description {
  margin: 0 0 24px 0;
  color: #909399;
  font-size: 14px;
}

/* 单条导入样式 */
.single-import-form {
  max-width: 600px;
}

/* 批量导入样式 */
.batch-import-section {
  max-width: 800px;
}

.upload-section {
  margin-bottom: 24px;
}

.preview-section {
  margin-top: 24px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preview-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

/* 数据生成样式 */
.generate-section {
  max-width: 800px;
}

.config-card {
  margin-bottom: 20px;
}

.generate-controls {
  margin: 24px 0;
  display: flex;
  gap: 12px;
}

.generated-results {
  margin-top: 24px;
}

.generated-results h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.generated-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-import-page {
    padding: 12px;
  }
  
  .preview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .preview-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style> 