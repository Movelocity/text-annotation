<template>
  <el-dialog
    v-model="dialogVisible"
    title=""
    width="500px"
    :before-close="handleClose"
    destroy-on-close
    class="modern-dialog"
  >
    <template #header>
      <div class="form-header">
        <div class="header-left">
          <i class="fas fa-plus"></i>
          <span class="header-title">新增标签</span>
          <el-tag type="primary" size="small">详细配置</el-tag>
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
        <el-form-item prop="label">
          <template #label>
            <div class="input-label">
              <i class="fas fa-tag"></i>
              <span>标签名称</span>
              <span class="required">*</span>
            </div>
          </template>
          <el-input
            v-model="form.label"
            placeholder="输入标签名称"
            :maxlength="50"
            show-word-limit
            clearable
            size="large"
            @keyup.enter="handleSubmit"
            autofocus
            class="modern-input"
          >
            <template #prefix>
              <i class="fas fa-tag input-icon"></i>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="description">
          <template #label>
            <div class="input-label">
              <i class="fas fa-align-left"></i>
              <span>标签描述</span>
              <span class="optional">(可选)</span>
            </div>
          </template>
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="可选，描述标签用途"
            :rows="3"
            :maxlength="200"
            show-word-limit
            class="modern-textarea"
          />
        </el-form-item>

        <el-form-item prop="groups">
          <template #label>
            <div class="input-label">
              <i class="fas fa-folder"></i>
              <span>分组</span>
              <span class="optional">(可选)</span>
            </div>
          </template>
          <el-select
            v-model="form.groups"
            placeholder="选择分组或输入新分组"
            filterable
            allow-create
            clearable
            size="large"
            style="width: 100%"
            class="modern-select"
          >
            <template #prefix>
              <i class="fas fa-folder input-icon"></i>
            </template>
            <el-option
              v-for="group in existingGroups"
              :key="group"
              :label="group"
              :value="group"
            >
              <div class="group-option">
                <i class="fas fa-folder-open"></i>
                <span>{{ group }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
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
          class="create-btn"
        >
          <i class="fas fa-plus"></i>
          {{ loading ? '创建中...' : '创建标签' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useLabelStore } from '@/stores/label'
import type { LabelCreate } from '@/types/api'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'created'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const labelStore = useLabelStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive<LabelCreate & { description?: string; groups?: string }>({
  label: '',
  description: '',
  groups: ''
})

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 获取现有分组
const existingGroups = computed(() => {
  const groups = new Set<string>()
  labelStore.labels.forEach(label => {
    if (label.groups) {
      groups.add(label.groups)
      // 也添加父级分组
      const parts = label.groups.split('/')
      for (let i = 1; i < parts.length; i++) {
        groups.add(parts.slice(0, i).join('/'))
      }
    }
  })
  return Array.from(groups).sort()
})

// 简化的表单验证规则
const rules: FormRules = {
  label: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '标签名称长度在 1 到 50 个字符', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value && labelStore.getLabelByName(value)) {
          callback(new Error('标签名称已存在'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const resetForm = () => {
  form.label = ''
  form.description = ''
  form.groups = ''
  formRef.value?.clearValidate()
}

const handleClose = () => {
  resetForm()
  dialogVisible.value = false
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    loading.value = true
    
    const labelData: LabelCreate = {
      label: form.label.trim(),
      description: form.description?.trim() || null,
      groups: form.groups?.trim() || null
    }

    await labelStore.createLabel(labelData)
    
    emit('created')
    handleClose()
    
  } catch (error) {
    if (error !== false) {
      ElMessage.error('创建标签失败，请重试')
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
</script>

<style scoped>
/* 复用快速创建的样式 */
.modern-dialog :deep(.el-dialog) {
  border-radius: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(64, 158, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.modern-dialog :deep(.el-dialog::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 50%, #e6a23c 100%);
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
  margin-bottom: 20px;
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
.modern-select,
.modern-textarea {
  transition: all 0.3s ease;
}

.modern-input :deep(.el-input__wrapper),
.modern-select :deep(.el-select__wrapper),
.modern-textarea :deep(.el-textarea__inner) {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  background: white;
}

.modern-input :deep(.el-input__wrapper:hover),
.modern-select :deep(.el-select__wrapper:hover),
.modern-textarea :deep(.el-textarea__inner:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
}

.modern-input :deep(.el-input__wrapper.is-focus),
.modern-select :deep(.el-select__wrapper.is-focused),
.modern-textarea :deep(.el-textarea__inner:focus) {
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

.group-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
}

.create-btn {
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

.create-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.create-btn:hover::before {
  left: 100%;
}

.create-btn:hover {
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