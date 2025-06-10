<template>
  <el-dialog
    v-model="dialogVisible"
    title="编辑标签"
    width="500px"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      @submit.prevent="handleSubmit"
    >
      <el-form-item label="标签名称" prop="label">
        <el-input
          v-model="form.label"
          placeholder="请输入标签名称"
          maxlength="50"
          show-word-limit
          clearable
          @keyup.enter="handleSubmit"
        />
        <div class="form-tip">
          标签名称应该简洁明了，便于识别和使用
        </div>
      </el-form-item>

      <el-form-item label="标签描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          placeholder="请输入标签描述（可选）"
          :rows="3"
          maxlength="200"
          show-word-limit
        />
        <div class="form-tip">
          可以添加标签的用途说明或使用场景
        </div>
      </el-form-item>

      <el-form-item label="标签分组" prop="groups">
        <el-input
          v-model="form.groups"
          placeholder="请输入分组路径，如：NLP/意图分析/情感"
          maxlength="100"
          show-word-limit
          clearable
        />
        <div class="form-tip">
          使用 "/" 分隔层级关系，如：NLP/意图分析/情感。留空表示未分组
        </div>
      </el-form-item>
    </el-form>

    <div class="dialog-tips">
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
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSubmit"
          :loading="loading"
        >
          保存更改
        </el-button>
      </div>
    </template>
  </el-dialog>
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
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.dialog-tips {
  margin-top: 16px;
}

.tips-list {
  margin: 0;
  padding-left: 16px;
}

.tips-list li {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input__count) {
  font-size: 11px;
}

:deep(.el-textarea__count) {
  font-size: 11px;
}
</style> 