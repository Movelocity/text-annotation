<template>
  <div class="data-import-page">
    <div class="page-header">
      <p>通过AI生成、手动创建或文件导入的方式添加标注数据</p>
    </div>

    <div class="content-container">
      <el-row :gutter="16">
        <!-- 左侧：数据输入区域 -->
        <el-col :span="8">
          <div class="work-panel input-panel">
            <div class="panel-header">
              <div class="panel-icon input-icon">
                <i class="fas fa-database"></i>
              </div>
              <h3>数据输入</h3>
              <div class="header-actions">
                <el-button size="small" @click="showApiConfig = true" v-if="activeInputTab === 'ai'">
                  <i class="fas fa-cog"></i> API配置
                </el-button>
              </div>
            </div>
            <div class="panel-content">
              <el-tabs v-model="activeInputTab" class="input-tabs">
                <!-- AI生成标签页 -->
                <el-tab-pane label="AI生成" name="ai">
                  <div class="tab-icon">
                    <i class="fas fa-brain"></i>
                  </div>
                  <div class="generation-params">
                    <el-form :model="generationParams" label-width="100px" size="default">
                      <el-form-item label="系统提示词">
                        <el-input v-model="generationParams.systemPrompt" type="textarea" :rows="2" />
                      </el-form-item>
                      <el-form-item label="用户提示词">
                        <el-input v-model="generationParams.userPrompt" type="textarea" :rows="2" />
                      </el-form-item>
                      <el-form-item label="生成数量">
                        <el-input-number v-model="generationParams.count" :min="1" :max="100" size="default" />
                      </el-form-item>
                      <el-form-item label="温度">
                        <el-slider v-model="generationParams.temperature" :min="0" :max="2" :step="0.1" :marks="temperatureMarks" />
                      </el-form-item>
                    </el-form>
                    
                    <div class="action-buttons">
                      <el-button @click="cancelGeneration" :disabled="!isGenerating" size="default">
                        <i class="fas fa-stop"></i> 取消
                      </el-button>
                      <el-button type="primary" @click="startGeneration" :loading="isGenerating" size="default">
                        <i class="fas fa-play"></i> 开始生成
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
                </el-tab-pane>

                <!-- 文件导入标签页 -->
                <el-tab-pane label="文件导入" name="file">
                  <div class="tab-icon">
                    <i class="fas fa-file-import"></i>
                  </div>
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
                      <div v-for="(line, index) in fileLines.slice(0, 5)" :key="index" class="preview-line">
                        {{ line }}
                      </div>
                      <div v-if="fileLines.length > 5" class="more-lines">
                        还有 {{ fileLines.length - 5 }} 条数据...
                      </div>
                    </div>
                    
                    <div class="action-buttons">
                      <el-button type="primary" @click="importFileToGenerated" size="small">
                        <i class="fas fa-arrow-right"></i> 导入到中间区域
                      </el-button>
                      <el-button @click="clearFile" size="small">
                        <i class="fas fa-times"></i> 取消
                      </el-button>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </el-col>

        <!-- 中间：生成数据展示区域 -->
        <el-col :span="8">
          <div class="work-panel display-panel">
            <div class="panel-header">
              <div class="panel-icon display-icon">
                <i class="fas fa-list-alt"></i>
              </div>
              <h3>生成结果 ({{ generatedTexts.length }})</h3>
              <div class="header-actions">
                <el-button size="small" @click="clearGeneratedTexts" :disabled="generatedTexts.length === 0">
                  <i class="fas fa-trash"></i> 清空
                </el-button>
              </div>
            </div>
            <div class="panel-content">
              <div class="display-list" v-if="generatedTexts.length > 0">
                <div v-for="(item, index) in generatedTexts" :key="item.id" class="display-item">
                  <div class="item-header">
                    <span class="item-number">#{{ index + 1 }}</span>
                    <el-button size="small" @click="copyText(item.text)" class="copy-btn">
                      <i class="fas fa-copy"></i> 复制
                    </el-button>
                  </div>
                  <div class="item-text-display">{{ item.text }}</div>
                  <div class="item-labels-display" v-if="item.labels">
                    <span class="labels-title">标签:</span>
                    <el-tag size="small" v-for="label in item.labels.split(',')" :key="label" class="label-tag">
                      {{ label.trim() }}
                    </el-tag>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <i class="fas fa-robot empty-icon"></i>
                <p>暂无生成数据</p>
                <p class="hint">使用左侧的AI生成或文件导入功能</p>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右侧：待提交数据区域 -->
        <el-col :span="8">
          <div class="work-panel submit-panel">
            <div class="panel-header">
              <div class="panel-icon submit-icon">
                <i class="fas fa-clipboard-list"></i>
              </div>
              <h3>待提交数据 ({{ pendingItems.length }})</h3>
              <div class="header-actions">
                <el-button size="small" @click="addNewItem" type="primary">
                  <i class="fas fa-plus"></i> 新增记录
                </el-button>
                <el-button size="small" @click="clearAllItems" :disabled="pendingItems.length === 0">
                  <i class="fas fa-trash"></i> 清空
                </el-button>
                <el-button size="small" @click="submitAllItems" :disabled="pendingItems.length === 0" :loading="isSubmitting" type="success">
                  <i class="fas fa-check"></i> 提交全部 ({{ pendingItems.length }})
                </el-button>
              </div>
            </div>
            <div class="panel-content">
              <div class="submit-list" v-if="pendingItems.length > 0">
                <div v-for="(item, index) in pendingItems" :key="item.id" class="submit-item">
                  <div class="item-index">{{ index + 1 }}</div>
                  <div class="item-content">
                    <el-input
                      v-model="item.text"
                      type="textarea"
                      :rows="2"
                      placeholder="输入文本内容..."
                      class="text-input"
                      size="small"
                    />
                    <el-input
                      v-model="item.labels"
                      placeholder="输入标签，用逗号分隔"
                      class="labels-input"
                      size="small"
                    />
                  </div>
                  <div class="item-actions">
                    <el-button size="small" type="danger" @click="removeItem(index)">
                      <i class="fas fa-trash"></i>
                    </el-button>
                    <el-button size="small" type="primary" @click="submitSingleItem(item, index)" :loading="item.isSubmitting">
                      <i class="fas fa-check"></i>
                    </el-button>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <i class="fas fa-inbox empty-icon"></i>
                <p>暂无待提交数据</p>
                <el-button @click="addNewItem" type="primary" size="small">
                  <i class="fas fa-plus"></i> 添加第一条记录
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- API配置弹窗 -->
    <el-dialog v-model="showApiConfig" title="API配置" width="500px">
      <el-form :model="generationConfig" label-width="120px" size="default">
        <el-form-item label="API Key" required>
          <el-input v-model="generationConfig.apiKey" type="password" placeholder="输入API Key" />
        </el-form-item>
        <el-form-item label="Base URL" required>
          <el-input v-model="generationConfig.baseUrl" placeholder="输入API Base URL" />
        </el-form-item>
        <el-form-item label="模型">
          <el-select v-model="generationConfig.model" placeholder="选择模型">
            <el-option label="gpt-4o-mini" value="gpt-4o-mini" />
            <el-option label="gpt-3.5-turbo" value="gpt-3.5-turbo" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showApiConfig = false">取消</el-button>
          <el-button type="primary" @click="saveApiConfig">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataGenerationService, type GenerationConfig, type GeneratedText } from '@/services/dataGeneration'

// 待提交数据项类型
interface PendingItem {
  id: string
  text: string
  labels: string
  isSubmitting?: boolean
}

// 生成的数据项类型
interface GeneratedItem {
  id: string
  text: string
  labels: string
  raw_output: string
}

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
  count: 1,
  temperature: 0.7
})
import type { CSSProperties } from 'vue'
interface Mark {
  style: CSSProperties
  label: string
}
type Marks = Record<number, Mark | string>
const temperatureMarks = reactive<Marks>({
  0: '0',
  0.5: '0.5',
  0.8: '0.8',
  1: {
    style: {
      color: '#1989FA',
    },
    label: '1.0',
  },
  2: '2',
})

// 状态
const isGenerating = ref(false)
const isSubmitting = ref(false)
const fileContent = ref('')
const fileLines = ref<string[]>([])
const currentTaskId = ref('')
const generationProgress = ref(0)
const generationMessage = ref('')
const showApiConfig = ref(false)
const pendingItems = ref<PendingItem[]>([])
const generatedTexts = ref<GeneratedItem[]>([])
const activeInputTab = ref('ai')

// EventSource 连接
let eventSource: EventSource | null = null

// 生成唯一ID
const generateId = () => Math.random().toString(36).substr(2, 9)

// 复制文本到剪贴板
const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('已复制到剪贴板')
  }
}

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
    generationConfig.value.apiKey = 'sk-xxx'
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

// 保存API配置
const saveApiConfig = () => {
  if (!generationConfig.value.apiKey || !generationConfig.value.baseUrl) {
    ElMessage.error('请填写API Key和Base URL')
    return
  }
  saveConfig()
  showApiConfig.value = false
  ElMessage.success('API配置已保存')
}

// 开始生成
const startGeneration = async () => {
  // 验证必填字段
  if (!generationConfig.value.apiKey || !generationConfig.value.baseUrl) {
    ElMessage.error('请先配置API参数')
    showApiConfig.value = true
    return
  }
  
  if (!generationParams.value.systemPrompt || !generationParams.value.userPrompt) {
    ElMessage.error('请填写系统提示词和用户提示词')
    return
  }
  
  try {
    isGenerating.value = true
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
        
        // 如果有新的生成文本，添加到待提交区
        if (data.latest_text) {
          addGeneratedItem(data.latest_text)
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

// 添加生成的项目到中间展示区域（修改原有的addGeneratedItem函数）
const addGeneratedItem = (text: GeneratedText) => {
  const item: GeneratedItem = {
    id: generateId(),
    text: text.text,
    labels: text.labels || '',
    raw_output: text.raw_output,
  }
  generatedTexts.value.unshift(item) // 新数据添加到顶部
}

// 清空生成的数据
const clearGeneratedTexts = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有生成的数据吗？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    generatedTexts.value = []
    ElMessage.success('已清空所有生成数据')
  } catch (error) {
    // 用户取消
  }
}

// 添加新项目
const addNewItem = () => {
  const item: PendingItem = {
    id: generateId(),
    text: '',
    labels: ''
  }
  pendingItems.value.push(item)
}

// 移除项目
const removeItem = (index: number) => {
  pendingItems.value.splice(index, 1)
}

// 清空所有项目
const clearAllItems = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有待提交数据吗？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    pendingItems.value = []
    ElMessage.success('已清空所有数据')
  } catch (error) {
    // 用户取消
  }
}

// 提交单个项目
const submitSingleItem = async (item: PendingItem, index: number) => {
  if (!item.text.trim()) {
    ElMessage.error('请输入文本内容')
    return
  }
  
  try {
    item.isSubmitting = true
    await dataGenerationService.createAnnotation({
      text: item.text,
      labels: item.labels
    })
    ElMessage.success('提交成功')
    pendingItems.value.splice(index, 1)
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    item.isSubmitting = false
  }
}

// 提交所有项目
const submitAllItems = async () => {
  const validItems = pendingItems.value.filter(item => item.text.trim())
  if (validItems.length === 0) {
    ElMessage.error('没有有效的数据可提交')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要提交 ${validItems.length} 条数据吗？`, '确认提交', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    isSubmitting.value = true
    let successCount = 0
    
    for (const item of validItems) {
      try {
        await dataGenerationService.createAnnotation({
          text: item.text,
          labels: item.labels
        })
        successCount++
      } catch (error) {
        console.error('提交项目失败:', error)
      }
    }
    
    ElMessage.success(`成功提交 ${successCount} 条数据`)
    pendingItems.value = pendingItems.value.filter(item => !item.text.trim())
    
  } catch (error) {
    // 用户取消
  } finally {
    isSubmitting.value = false
  }
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

// 清空文件
const clearFile = () => {
  fileContent.value = ''
  fileLines.value = []
}

// 将文件导入到生成数据展示区域（修改原有的importFileToQueue函数）
const importFileToGenerated = () => {
  if (fileLines.value.length === 0) {
    ElMessage.error('请先选择文件')
    return
  }
  
  const newItems = fileLines.value.map(line => ({
    id: generateId(),
    text: line.trim(),
    labels: '',
    raw_output: line.trim(), // 文件导入时，raw_output就是原始文本
  }))
  
  generatedTexts.value.unshift(...newItems) // 新数据添加到顶部
  ElMessage.success(`已添加 ${newItems.length} 条数据到生成数据区域`)
  clearFile()
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
  max-width: 1700px;
  margin: 0 auto;
}

.work-panel {
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  transition: all 0.2s ease;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.work-panel:hover {
  /* border-color: #c0c4cc; */
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  color: #2c3e50;
}

.display-item.selected {
  background: #e8f4ff;
  border-color: #409EFF;
}

.display-item .item-content {
  cursor: pointer;
}

.batch-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.submit-list {
  max-height: calc(100vh - 450px);
  overflow-y: auto;
}

.submit-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  background: #fafafa;
  transition: all 0.2s ease;
}

.submit-item:hover {
  background: #f0f9ff;
  border-color: #409EFF;
}

.item-index {
  width: 32px;
  height: 32px;
  background: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 4px;
}

.panel-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 50%;
  margin-right: 12px;
  font-size: 16px;
  color: #409EFF;
}

.input-icon {
  background: rgba(255, 107, 107, 0.1);
  color: #FF6B6B;
}

.display-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.submit-icon {
  background: rgba(78, 205, 196, 0.1);
  color: #4ECDC4;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.2em;
  font-weight: 600;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.panel-content {
  padding: 20px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.input-tabs {
  margin-bottom: 16px;
}

.tab-icon {
  text-align: center;
  margin-bottom: 16px;
}

.generation-params {
  margin-bottom: 24px;
}

.action-buttons {
  margin-top: 2rem;
  display: flex;
  justify-content: end;
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

.display-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.display-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  background: #fafafa;
  transition: all 0.2s ease;
}

.display-item:hover {
  background: #f0f9ff;
  border-color: #c0c4cc;
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.item-number {
  font-weight: bold;
  color: #666;
  font-size: 14px;
}

.copy-btn {
  padding: 4px 12px;
  font-size: 12px;
}

.item-text-display {
  margin-bottom: 12px;
  line-height: 1.3;
  font-size: 14px;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.item-labels-display {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.labels-title {
  font-weight: 600;
  color: #666;
  font-size: 12px;
}

.label-tag {
  margin: 0;
}

.text-input {
  margin-bottom: 8px;
}

.labels-input {
  margin-bottom: 0;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 64px;
  color: #ddd;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 20px;
}

.hint {
  font-size: 14px;
  color: #999;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 滚动条样式 */
.display-list::-webkit-scrollbar,
.submit-list::-webkit-scrollbar {
  width: 6px;
}

.display-list::-webkit-scrollbar-track,
.submit-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.display-list::-webkit-scrollbar-thumb,
.submit-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.display-list::-webkit-scrollbar-thumb:hover,
.submit-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 