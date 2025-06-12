<template>
  <div class="data-import-page">
    <div class="page-header">
      <h1><i class="fas fa-upload"></i> 数据导入</h1>
      <p>通过AI生成、手动创建或文件导入的方式添加标注数据</p>
    </div>

    <div class="content-container">
      <el-row :gutter="24">
        <!-- 数据生成区域 -->
        <el-col :span="12">
          <div class="section-card">
            <div class="card-header">
              <div class="card-icon generation-icon">
                <i class="fas fa-brain"></i>
              </div>
              <h3>AI数据生成</h3>
            </div>
            <div class="card-content">
              <!-- API配置 -->
              <div class="config-section">
                <h4><i class="fas fa-cog"></i> API配置</h4>
                <el-form :model="generationConfig" label-width="120px" size="default">
                  <el-form-item label="API Key">
                    <el-input v-model="generationConfig.apiKey" type="password" placeholder="输入API Key" />
                  </el-form-item>
                  <el-form-item label="Base URL">
                    <el-input v-model="generationConfig.baseUrl" placeholder="输入API Base URL" />
                  </el-form-item>
                  <el-form-item label="模型">
                    <el-select v-model="generationConfig.model" placeholder="选择模型">
                      <el-option label="gpt-4o-mini" value="gpt-4o-mini" />
                      <el-option label="gpt-3.5-turbo" value="gpt-3.5-turbo" />
                    </el-select>
                  </el-form-item>
                </el-form>
              </div>
              
              <!-- 生成参数 -->
              <div class="generation-params">
                <h4><i class="fas fa-magic"></i> 生成参数</h4>
                <el-form :model="generationParams" label-width="120px" size="default">
                  <el-form-item label="系统提示词">
                    <el-input v-model="generationParams.systemPrompt" type="textarea" :rows="3" />
                  </el-form-item>
                  <el-form-item label="用户提示词">
                    <el-input v-model="generationParams.userPrompt" type="textarea" :rows="3" />
                  </el-form-item>
                  <el-form-item label="生成数量">
                    <el-input-number v-model="generationParams.count" :min="1" :max="100" />
                  </el-form-item>
                  <el-form-item label="温度">
                    <el-slider v-model="generationParams.temperature" :min="0" :max="2" :step="0.1" />
                  </el-form-item>
                </el-form>
                
                <div class="action-buttons">
                  <el-button type="primary" @click="startGeneration" :loading="isGenerating">
                    <i class="fas fa-play"></i> 开始生成
                  </el-button>
                  <el-button @click="cancelGeneration" :disabled="!isGenerating">
                    <i class="fas fa-stop"></i> 取消
                  </el-button>
                </div>
                
                <!-- 生成进度 -->
                <div class="generation-progress" v-if="isGenerating || generationProgress > 0">
                  <div class="progress-info">
                    <span>生成进度: {{ generationProgress }}%</span>
                    <span v-if="generationMessage">{{ generationMessage }}</span>
                  </div>
                  <el-progress :percentage="generationProgress" :status="isGenerating ? undefined : 'success'" />
                </div>
              </div>
              
              <!-- 生成结果 -->
              <div class="generation-output" v-if="generatedTexts.length > 0">
                <h4><i class="fas fa-list"></i> 生成结果</h4>
                <div class="result-list">
                  <div v-for="(text, index) in generatedTexts" :key="index" class="result-item">
                    <div class="result-content">{{ text.text }}</div>
                    <div class="result-actions">
                      <el-button size="small" @click="createFromResult(text)">
                        <i class="fas fa-plus"></i> 创建
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 手动创建区域 -->
        <el-col :span="12">
          <div class="section-card">
            <div class="card-header">
              <div class="card-icon manual-icon">
                <i class="fas fa-edit"></i>
              </div>
              <h3>手动创建</h3>
            </div>
            <div class="card-content">
              <el-form :model="manualForm" label-width="80px" size="default">
                <el-form-item label="文本内容">
                  <el-input
                    v-model="manualForm.text"
                    type="textarea"
                    :rows="6"
                    placeholder="输入要标注的文本内容..."
                  />
                </el-form-item>
                <el-form-item label="标签">
                  <el-input
                    v-model="manualForm.labels"
                    placeholder="输入标签，用逗号分隔"
                  />
                </el-form-item>
              </el-form>
              
              <div class="action-buttons">
                <el-button type="primary" @click="createManualAnnotation" :loading="isCreating">
                  <i class="fas fa-plus"></i> 创建标注
                </el-button>
                <el-button @click="clearManualForm">
                  <i class="fas fa-trash"></i> 清空
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="24" style="margin-top: 24px;">
        <!-- 文件导入区域 -->
        <el-col :span="24">
          <div class="section-card">
            <div class="card-header">
              <div class="card-icon import-icon">
                <i class="fas fa-file-import"></i>
              </div>
              <h3>文件导入</h3>
            </div>
            <div class="card-content">
              <div class="upload-area">
                <el-upload
                  class="upload-dragger"
                  drag
                  action="#"
                  :auto-upload="false"
                  :on-change="handleFileChange"
                  :show-file-list="false"
                >
                  <i class="fas fa-cloud-upload-alt upload-icon"></i>
                  <div class="el-upload__text">
                    将文件拖到此处，或<em>点击上传</em>
                  </div>
                  <div class="el-upload__tip">
                    支持 .txt 文件，每行一条数据
                  </div>
                </el-upload>
              </div>
              
              <div class="file-preview" v-if="fileContent">
                <h4><i class="fas fa-eye"></i> 文件预览</h4>
                <div class="preview-stats">
                  <el-tag>共 {{ fileLines.length }} 条数据</el-tag>
                </div>
                <div class="preview-content">
                  <div v-for="(line, index) in fileLines.slice(0, 10)" :key="index" class="preview-line">
                    {{ line }}
                  </div>
                  <div v-if="fileLines.length > 10" class="more-lines">
                    还有 {{ fileLines.length - 10 }} 条数据...
                  </div>
                </div>
                
                <div class="action-buttons">
                  <el-button type="primary" @click="importFile" :loading="isImporting">
                    <i class="fas fa-file-import"></i> 导入数据
                  </el-button>
                  <el-button @click="clearFile">
                    <i class="fas fa-times"></i> 取消
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataGenerationService, type GenerationConfig, type GeneratedText } from '@/services/dataGeneration'

// 生成配置
const generationConfig = ref({
  apiKey: '',
  baseUrl: '',
  model: 'gpt-4o-mini'
})

// 生成参数
const generationParams = ref({
  systemPrompt: '',
  userPrompt: '',
  count: 10,
  temperature: 0.7
})

// 手动创建表单
const manualForm = ref({
  text: '',
  labels: ''
})

// 状态
const isGenerating = ref(false)
const isCreating = ref(false)
const isImporting = ref(false)
const generatedTexts = ref<GeneratedText[]>([])
const fileContent = ref('')
const fileLines = ref<string[]>([])
const currentTaskId = ref('')
const generationProgress = ref(0)
const generationMessage = ref('')

// EventSource 连接
let eventSource: EventSource | null = null

// 从localStorage加载配置
const loadConfig = () => {
  const config = dataGenerationService.loadConfig()
  if (Object.keys(config).length > 0) {
    generationConfig.value.apiKey = config.apiKey || ''
    generationConfig.value.baseUrl = config.baseUrl || ''
    generationConfig.value.model = config.model || 'gpt-4o-mini'
    generationParams.value.systemPrompt = config.systemPrompt || ''
    generationParams.value.userPrompt = config.userPrompt || ''
    generationParams.value.temperature = config.temperature || 0.7
  } else {
    // 使用用户提供的默认配置
    generationConfig.value.apiKey = 'sk-s7TtH0vgnkWqUjk06bC77e9eE8F54c2a80243bC8044dAdA5'
    generationConfig.value.baseUrl = 'https://nekoapi.com/v1'
    generationConfig.value.model = 'gpt-4o-mini'
    generationParams.value.systemPrompt = '你是一个AI助手，专门用于生成需要标注的文本数据。'
    generationParams.value.userPrompt = '请生成一段需要进行意图识别标注的对话文本。'
    generationParams.value.temperature = 0.7
  }
}

// 保存配置到localStorage
const saveConfig = () => {
  const config: GenerationConfig = {
    apiKey: generationConfig.value.apiKey,
    baseUrl: generationConfig.value.baseUrl,
    model: generationConfig.value.model,
    systemPrompt: generationParams.value.systemPrompt,
    userPrompt: generationParams.value.userPrompt,
    count: generationParams.value.count,
    temperature: generationParams.value.temperature
  }
  dataGenerationService.saveConfig(config)
}

// 开始生成
const startGeneration = async () => {
  // 验证必填字段
  if (!generationConfig.value.apiKey || !generationConfig.value.baseUrl) {
    ElMessage.error('请填写API Key和Base URL')
    return
  }
  
  if (!generationParams.value.systemPrompt || !generationParams.value.userPrompt) {
    ElMessage.error('请填写系统提示词和用户提示词')
    return
  }
  
  try {
    isGenerating.value = true
    generatedTexts.value = []
    generationProgress.value = 0
    
    // 保存配置
    saveConfig()
    
    // 启动生成任务
    const config: GenerationConfig = {
      apiKey: generationConfig.value.apiKey,
      baseUrl: generationConfig.value.baseUrl,
      model: generationConfig.value.model,
      systemPrompt: generationParams.value.systemPrompt,
      userPrompt: generationParams.value.userPrompt,
      count: generationParams.value.count,
      temperature: generationParams.value.temperature
    }
    
    const task = await dataGenerationService.startGeneration(config)
    currentTaskId.value = task.task_id
    
    // 创建 EventSource 监听生成进度
    eventSource = dataGenerationService.createGenerationStream(task.task_id)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.error) {
          ElMessage.error(data.error)
          return
        }
        
        generationProgress.value = data.progress || 0
        generationMessage.value = data.message || ''
        
        // 如果有新的生成文本
        if (data.latest_text) {
          generatedTexts.value.push(data.latest_text)
        }
        
        // 生成完成或取消
        if (data.status === 'completed' || data.status === 'cancelled' || data.status === 'error') {
          isGenerating.value = false
          if (eventSource) {
            eventSource.close()
            eventSource = null
          }
          
          if (data.status === 'completed') {
            ElMessage.success(`生成完成！共生成 ${data.current_count} 条数据`)
          } else if (data.status === 'cancelled') {
            ElMessage.warning('生成已取消')
          } else if (data.status === 'error') {
            ElMessage.error(`生成失败: ${data.error}`)
          }
        }
      } catch (e) {
        console.error('解析生成数据失败:', e)
      }
    }
    
    eventSource.onerror = (error) => {
      console.error('EventSource 错误:', error)
      isGenerating.value = false
      if (eventSource) {
        eventSource.close()
        eventSource = null
      }
      ElMessage.error('连接生成服务失败')
    }
    
  } catch (error: any) {
    console.error('启动生成失败:', error)
    isGenerating.value = false
    ElMessage.error(error.message || '启动生成失败')
  }
}

// 取消生成
const cancelGeneration = async () => {
  if (!currentTaskId.value) return
  
  try {
    await dataGenerationService.cancelGeneration(currentTaskId.value)
    isGenerating.value = false
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    ElMessage.success('已取消生成')
  } catch (error: any) {
    console.error('取消生成失败:', error)
    ElMessage.error('取消生成失败')
  }
}

// 从生成结果创建
const createFromResult = async (text: GeneratedText) => {
  try {
    await dataGenerationService.createAnnotation({
      text: text.text,
      labels: text.labels || ''
    })
    ElMessage.success('创建标注成功')
  } catch (error: any) {
    console.error('创建标注失败:', error)
    ElMessage.error('创建标注失败')
  }
}

// 手动创建标注
const createManualAnnotation = async () => {
  if (!manualForm.value.text.trim()) {
    ElMessage.error('请输入文本内容')
    return
  }
  
  try {
    isCreating.value = true
    await dataGenerationService.createAnnotation({
      text: manualForm.value.text,
      labels: manualForm.value.labels
    })
    ElMessage.success('创建标注成功')
    clearManualForm()
  } catch (error: any) {
    console.error('创建标注失败:', error)
    ElMessage.error('创建标注失败')
  } finally {
    isCreating.value = false
  }
}

// 清空手动表单
const clearManualForm = () => {
  manualForm.value.text = ''
  manualForm.value.labels = ''
}

// 处理文件变化
const handleFileChange = (file: any) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    fileContent.value = e.target?.result as string
    fileLines.value = fileContent.value.split('\n').filter(line => line.trim())
  }
  reader.readAsText(file.raw)
}

// 导入文件
const importFile = async () => {
  if (fileLines.value.length === 0) {
    ElMessage.error('请先选择文件')
    return
  }
  
  try {
    const result = await ElMessageBox.confirm(
      `确定要导入 ${fileLines.value.length} 条数据吗？`,
      '确认导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (result === 'confirm') {
      isImporting.value = true
      const response = await dataGenerationService.importTexts(fileLines.value)
      ElMessage.success(`成功导入 ${response.imported_count} 条数据`)
      clearFile()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('导入文件失败:', error)
      ElMessage.error('导入文件失败')
    }
  } finally {
    isImporting.value = false
  }
}

// 清空文件
const clearFile = () => {
  fileContent.value = ''
  fileLines.value = []
}

// 清理资源
onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
})

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.data-import-page {
  padding: 24px;
  min-height: calc(100vh - 200px);
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 2.5em;
  font-weight: 300;
}

.page-header p {
  color: #7f8c8d;
  font-size: 1.1em;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
}

.section-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.2s ease;
}

.section-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  margin-right: 16px;
  font-size: 18px;
}

.generation-icon {
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
}

.manual-icon {
  background: linear-gradient(135deg, #4ECDC4, #44A08D);
}

.import-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.card-header h3 {
  margin: 0;
  font-size: 1.4em;
  font-weight: 500;
}

.card-content {
  padding: 24px;
}

.config-section,
.generation-params,
.generation-output {
  margin-bottom: 24px;
}

.config-section h4,
.generation-params h4,
.generation-output h4 {
  color: #2c3e50;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.upload-area {
  margin-bottom: 24px;
}

.upload-dragger {
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.file-preview {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
}

.preview-stats {
  margin-bottom: 16px;
}

.preview-content {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  padding: 12px;
  background: #fafafa;
}

.preview-line {
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.more-lines {
  text-align: center;
  color: #999;
  padding: 8px 0;
  font-style: italic;
}

.result-list {
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 8px;
  background: #fafafa;
}

.result-content {
  flex: 1;
  margin-right: 12px;
  font-size: 14px;
}

.el-form-item {
  margin-bottom: 18px;
}

.el-slider {
  margin: 0 12px;
}

.generation-progress {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}
</style> 