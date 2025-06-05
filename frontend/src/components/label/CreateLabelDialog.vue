<template>
  <el-dialog
    v-model="dialogVisible"
    title="新增标签"
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
    </el-form>

    <div class="dialog-tips">
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        show-icon
      >
        <ul class="tips-list">
          <li>标签名称不能重复</li>
          <li>建议使用有意义的标签名称</li>
          <li>创建后可以在标注时使用该标签</li>
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
          确定创建
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

const form = reactive<LabelCreate & { description?: string }>({
  label: '',
  description: ''
})

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表单验证规则
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
      description: form.description?.trim() || null
    }

    await labelStore.createLabel(labelData)
    
    emit('created')
    handleClose()
    
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
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
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.dialog-tips {
  margin: 20px 0;
}

.tips-list {
  margin: 0;
  padding-left: 16px;
  font-size: 13px;
  color: #606266;
}

.tips-list li {
  margin-bottom: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-dialog__header) {
  padding: 20px 20px 10px;
}

:deep(.el-dialog__body) {
  padding: 10px 20px 20px;
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-alert__content) {
  padding-left: 8px;
}
</style> 