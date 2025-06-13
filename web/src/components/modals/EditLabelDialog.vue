<template>
  <div>
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
            <i class="fas fa-edit"></i>
            <span class="header-title">编辑标签</span>
            <el-tag type="warning" size="small">修改配置</el-tag>
          </div>
        </div>
      </template>

      <div class="form-content">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="handleSubmit"
          class="modern-form"
        >
          <el-form-item label="标签名称" prop="label">
            <el-input
              v-model="form.label"
              placeholder="请输入标签名称"
              maxlength="50"
              show-word-limit
              clearable
              size="large"
              @keyup.enter="handleSubmit"
              class="modern-input"
            >
              <template #prefix>
                <i class="fas fa-tag input-icon"></i>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="标签描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              placeholder="请输入标签描述（可选）"
              :rows="3"
              maxlength="200"
              show-word-limit
              class="modern-textarea"
            />
          </el-form-item>

          <el-form-item label="标签分组" prop="groups">
            <el-input
              v-model="form.groups"
              placeholder="请输入分组路径，如：NLP/意图分析/情感"
              maxlength="100"
              show-word-limit
              clearable
              size="large"
              class="modern-input"
            >
              <template #prefix>
                <i class="fas fa-folder input-icon"></i>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
        >
          <ul class="tips-list">
            <li>标签名称不能与其他标签重复</li>
            <li>分组路径区分大小写</li>
            <li>修改后会影响所有使用该标签的标注数据</li>
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
            {{ loading ? '保存中...' : '保存更改' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useLabelStore } from '@/stores/label'
import type { LabelResponse, LabelUpdate } from '@/types/api'

interface Props {
  modelValue: boolean
  label: LabelResponse | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'updated'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const labelStore = useLabelStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const form = reactive({
  label: '',
  description: '',
  groups: ''
})

// 对话框显示状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表单验证规则
const rules: FormRules = {
  label: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '标签名称长度应在 1 到 50 个字符', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (!props.label) {
          callback()
          return
        }
        
        // 检查是否与其他标签重复（排除自己）
        const existingLabel = labelStore.labels.find(
          l => l.label === value && l.id !== props.label!.id
        )
        if (existingLabel) {
          callback(new Error('标签名称已存在'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  description: [
    { max: 200, message: '描述长度不能超过 200 个字符', trigger: 'blur' }
  ],
  groups: [
    { max: 100, message: '分组路径长度不能超过 100 个字符', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (!value) {
          callback()
          return
        }
        
        // 验证分组路径格式
        const groupParts = value.split('/')
        const isValid = groupParts.every((part: string) => {
          const trimmed = part.trim()
          return trimmed.length > 0 && trimmed.length <= 20
        })
        
        if (!isValid) {
          callback(new Error('分组路径格式不正确，每级分组不能为空且不超过20字符'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    label: '',
    description: '',
    groups: ''
  })
}

// 初始化表单数据
const initForm = () => {
  if (props.label) {
    Object.assign(form, {
      label: props.label.label || '',
      description: props.label.description || '',
      groups: props.label.groups || ''
    })
  }
}

// 处理关闭
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value || !props.label) return
  
  try {
    // 验证表单
    await formRef.value.validate()
    
    loading.value = true
    
    // 准备更新数据
    const updateData: LabelUpdate = {
      label: form.label.trim(),
      description: form.description.trim() || null,
      groups: form.groups.trim() || null
    }
    
    // 调用更新接口
    await labelStore.updateLabel(props.label.id, updateData)
    
    ElMessage.success('标签更新成功')
    emit('updated')
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    console.error('更新标签失败:', error)
    ElMessage.error('更新标签失败')
  } finally {
    loading.value = false
  }
}

// 监听标签变化，初始化表单
watch(() => props.label, (newLabel) => {
  if (newLabel && props.modelValue) {
    initForm()
  }
}, { immediate: true })

// 监听对话框打开状态
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.label) {
    initForm()
  } else if (!isOpen) {
    resetForm()
  }
})
</script>

<style scoped>
/* 现代化对话框样式。
scope样式使用时，需要在 el-dialog 外面套一层div，
然后才能使用 :deep(.modern-dialog) 选择器 */
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
  color: #e6a23c;
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

.modern-input,
.modern-textarea {
  transition: all 0.3s ease;
}

.modern-input :deep(.el-input__wrapper),
.modern-textarea :deep(.el-textarea__inner) {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  background: white;
}

.modern-input :deep(.el-input__wrapper:hover),
.modern-textarea :deep(.el-textarea__inner:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
}

.modern-input :deep(.el-input__wrapper.is-focus),
.modern-textarea :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.input-icon {
  color: #95a5a6;
  transition: color 0.3s ease;
}

.modern-input :deep(.el-input__wrapper.is-focus) .input-icon {
  color: #409eff;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.4;
  padding-left: 12px;
  border-left: 3px solid #e4e7ed;
  background: rgba(244, 244, 245, 0.5);
  padding: 6px 12px;
  border-radius: 4px;
}

.dialog-tips {
  margin-top: 20px;
  padding: 16px;
  background: rgba(144, 147, 153, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(144, 147, 153, 0.1);
}

.tips-list {
  margin: 0;
  padding-left: 16px;
}

.tips-list li {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 4px;
  color: #606266;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
}

.save-btn {
  background: linear-gradient(135deg, #e6a23c 0%, #f39c12 100%);
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
  box-shadow: 0 8px 25px rgba(230, 162, 60, 0.3);
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
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__count) {
  font-size: 11px;
}

:deep(.el-textarea__count) {
  font-size: 11px;
}

:deep(.el-alert) {
  border-radius: 8px;
  border: none;
  background: rgba(64, 158, 255, 0.05);
}

:deep(.el-alert__icon) {
  color: #409eff;
}

:deep(.el-alert__title) {
  color: #2c3e50;
  font-weight: 600;
}
</style> 