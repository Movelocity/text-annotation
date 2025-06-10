<template>
  <el-dialog
    v-model="dialogVisible"
    title="新增标签"
    width="450px"
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
          placeholder="输入标签名称"
          maxlength="50"
          clearable
          @keyup.enter="handleSubmit"
          autofocus
        />
      </el-form-item>

      <el-form-item label="标签描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          placeholder="可选，描述标签用途"
          :rows="2"
          maxlength="200"
        />
      </el-form-item>

      <el-form-item label="分组" prop="groups">
        <el-select
          v-model="form.groups"
          placeholder="选择分组或输入新分组"
          filterable
          allow-create
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="group in existingGroups"
            :key="group"
            :label="group"
            :value="group"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSubmit"
          :loading="loading"
        >
          创建
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
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-dialog__header) {
  padding: 20px 20px 10px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style> 