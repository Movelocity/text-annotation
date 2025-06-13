<template>
  <div>
    <el-dialog
      v-model="dialogVisible"
      title=""
      width="520px"
      :before-close="handleClose"
      destroy-on-close
      class="modern-dialog"
    >
      <template #header>
        <div class="form-header">
          <div class="header-left">
            <i class="fas fa-cog"></i>
            <span class="header-title">API配置</span>
            <el-tag type="info" size="small">AI生成设置</el-tag>
          </div>
        </div>
      </template>

      <div class="form-content">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleSubmit"
          class="modern-form"
        >
          <el-form-item prop="baseUrl">
            <template #label>
              <div class="input-label">
                <i class="fas fa-link"></i>
                <span>Base URL</span>
                <span class="required">*</span>
              </div>
            </template>
            <el-input
              v-model="form.baseUrl"
              placeholder="输入API Base URL"
              clearable
              size="large"
              class="modern-input"
            >
              <template #prefix>
                <i class="fas fa-link input-icon"></i>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="apiKey">
            <template #label>
              <div class="input-label">
                <i class="fas fa-key"></i>
                <span>API Key</span>
                <span class="required">*</span>
              </div>
            </template>
            <el-input
              v-model="form.apiKey"
              type="password"
              placeholder="输入API Key"
              show-password
              clearable
              size="large"
              class="modern-input"
            >
              <template #prefix>
                <i class="fas fa-key input-icon"></i>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="model">
            <template #label>
              <div class="input-label">
                <i class="fas fa-brain"></i>
                <span>模型</span>
                <span class="optional">(可选或自定义)</span>
              </div>
            </template>
            <el-select
              v-model="form.model"
              placeholder="选择或输入模型名"
              clearable
              filterable
              allow-create
              default-first-option
              size="large"
              style="width: 100%"
              class="modern-select"
            >
              <template #prefix>
                <i class="fas fa-brain input-icon"></i>
              </template>
              <el-option
                v-for="modelOption in modelOptions"
                :key="modelOption.value"
                :label="modelOption.value"
                :value="modelOption.value"
              >
                <div class="model-option">
                  <i class="fas fa-robot"></i>
                  <span>{{ modelOption.value }}</span>
                  <span class="model-desc">{{ modelOption.description }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>

        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
          class="config-tips"
        >
          <ul class="tips-list">
            <li>API Key用于身份认证，请妥善保管</li>
            <li>Base URL为API服务地址，确保网络可达</li>
            <li>模型可选择预设选项或手动输入任意模型名</li>
            <li>配置将保存在本地浏览器中</li>
          </ul>
        </el-alert>
      </div>

      <template #footer>
        <div class="form-actions">
          <el-button @click="handleClose" size="large" class="cancel-btn">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="handleSubmit"
            :loading="loading"
            size="large"
            class="save-btn"
          >
            <i class="fas fa-save"></i>
            {{ loading ? '保存中...' : '保存配置' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

interface ApiConfig {
  apiKey: string
  baseUrl: string
  model: string
}

interface Props {
  modelValue: boolean
  config: ApiConfig
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', config: ApiConfig): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const form = reactive<ApiConfig>({
  apiKey: '',
  baseUrl: '',
  model: 'gpt-4o-mini'
})

// 模型选项
const modelOptions = [
  {
    value: 'gpt-4o-mini',
    description: '快速且经济'
  },
  {
    value: 'gpt-4o',
    description: '高质量多模态'
  },
  {
    value: 'gpt-3.5-turbo',
    description: '平衡性能'
  },
  {
    value: 'claude-3-sonnet',
    description: '高质量推理'
  },
  {
    value: 'claude-3-haiku',
    description: '快速响应'
  },
  {
    value: 'deepseek-chat',
    description: '高性价比'
  },
  {
    value: 'qwen-max',
    description: '阿里通义千问'
  }
]

// 对话框显示状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表单验证规则
const rules: FormRules = {
  apiKey: [
    { required: true, message: '请输入API Key', trigger: 'blur' },
    { min: 10, message: 'API Key长度不能少于10个字符', trigger: 'blur' }
  ],
  baseUrl: [
    { required: true, message: '请输入Base URL', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (!value) {
          callback()
          return
        }
        
        try {
          new URL(value)
          callback()
        } catch {
          callback(new Error('请输入有效的URL格式'))
        }
      },
      trigger: 'blur'
    }
  ]
}

// 重置表单
const resetForm = () => {
  form.apiKey = props.config.apiKey || ''
  form.baseUrl = props.config.baseUrl || ''
  form.model = props.config.model || 'gpt-4o-mini'
  formRef.value?.clearValidate()
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    loading.value = true
    
    const configData: ApiConfig = {
      apiKey: form.apiKey.trim(),
      baseUrl: form.baseUrl.trim(),
      model: form.model
    }

    // 简单验证API连接（这里可以添加实际的API测试）
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('save', configData)
    ElMessage.success('API配置已保存')
    handleClose()
    
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存配置失败，请检查输入')
    }
  } finally {
    loading.value = false
  }
}

// 监听对话框打开，重置表单
watch(dialogVisible, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

// 监听配置变化，更新表单
watch(() => props.config, () => {
  if (dialogVisible.value) {
    resetForm()
  }
}, { deep: true })
</script>

<style scoped>
/* 复用快速创建的样式 */
:deep(.modern-dialog) {
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(64, 158, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.modern-dialog :deep(.el-dialog__header) {
  padding: 24px 24px 0;
  border-bottom: none;
}

.modern-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.modern-dialog :deep(.el-dialog__footer) {
  padding: 0 24px 24px;
  border-top: none;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(64, 158, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left i {
  color: #409eff;
  font-size: 18px;
}

.header-title {
  font-weight: 700;
  color: #2c3e50;
  font-size: 18px;
  letter-spacing: -0.5px;
}

.form-content {
  margin-bottom: 20px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.required {
  color: #e74c3c;
  font-weight: 700;
}

.optional {
  color: #95a5a6;
  font-size: 12px;
  font-weight: 400;
}

.modern-input,
.modern-select {
  transition: all 0.3s ease;
}

.modern-input :deep(.el-input__wrapper),
.modern-select :deep(.el-select__wrapper) {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  background: white;
}

.modern-input :deep(.el-input__wrapper:hover),
.modern-select :deep(.el-select__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
}

.modern-input :deep(.el-input__wrapper.is-focus),
.modern-select :deep(.el-select__wrapper.is-focused) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.input-icon {
  color: #95a5a6;
  transition: color 0.3s ease;
}

.modern-input :deep(.el-input__wrapper.is-focus) .input-icon,
.modern-select :deep(.el-select__wrapper.is-focused) .input-icon {
  color: #409eff;
}

.model-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-desc {
  color: #95a5a6;
  font-size: 12px;
  margin-left: auto;
}

.config-tips {
  margin-top: 16px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.tips-list {
  margin: 0;
  padding-left: 16px;
  color: #1e40af;
}

.tips-list li {
  margin-bottom: 4px;
  font-size: 13px;
  line-height: 1.4;
}

.tips-list li:last-child {
  margin-bottom: 0;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
}

.save-btn {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  border: none;
  color: white;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.save-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.save-btn:hover::before {
  left: 100%;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.3);
}

.cancel-btn {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  color: #495057;
  font-weight: 500;
  padding: 12px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-form-item__label) {
  display: none;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style> 