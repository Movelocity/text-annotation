<template>
  <div class="label-manage-page">
    <!-- 页面头部 -->
    <PageHeader
      title="标签管理"
      title-icon="fas fa-tags"
      :breadcrumbs="breadcrumbs"
      :stats="headerStats"
      home-route="/pages/home"
    >
    </PageHeader>

    <div class="create-btn-section">
      <div class="create-actions">
        <ModernButton
          text="新增标签"
          icon="fas fa-plus"
          type="primary"
          :loading="labelStore.loading"
          @click="showCreateDialog = true"
        />
        <el-button 
          link 
          @click="showQuickCreate = !showQuickCreate"
          :icon="showQuickCreate ? ArrowUp : ArrowDown"
        >
          快速创建
        </el-button>
      </div>
      
      <!-- 快速创建表单 -->
      <el-collapse-transition>
        <div v-show="showQuickCreate" class="quick-create-form">
          <el-form
            ref="quickFormRef"
            :model="quickForm"
            :rules="quickRules"
            layout="inline"
            @submit.prevent="handleQuickCreate"
          >
            <el-form-item prop="label" style="margin-bottom: 0;">
              <el-input
                v-model="quickForm.label"
                placeholder="标签名称"
                style="width: 200px;"
                @keyup.enter="handleQuickCreate"
                clearable
              />
            </el-form-item>
            <el-form-item prop="groups" style="margin-bottom: 0;">
              <el-select
                v-model="quickForm.groups"
                placeholder="选择分组"
                filterable
                allow-create
                clearable
                style="width: 160px;"
              >
                <el-option
                  v-for="group in availableGroups"
                  :key="group"
                  :label="group || '未分组'"
                  :value="group"
                />
              </el-select>
            </el-form-item>
            <el-form-item style="margin-bottom: 0;">
              <el-button 
                type="primary" 
                @click="handleQuickCreate"
                :loading="quickCreating"
                size="default"
              >
                创建
              </el-button>
              <el-button @click="resetQuickForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-collapse-transition>
    </div>

    <!-- 搜索和过滤 -->
    <div class="search-section">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索标签名称或描述..."
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="selectedGroup" placeholder="选择分组" @change="handleGroupFilter" clearable>
            <el-option label="全部分组" value="" />
            <el-option 
              v-for="group in availableGroups" 
              :key="group" 
              :label="group || '未分组'" 
              :value="group || ''" 
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="sortBy" placeholder="排序方式" @change="handleSortChange">
            <el-option label="按使用频率排序" value="usage" />
            <el-option label="按名称排序" value="name" />
            <el-option label="按分组排序" value="group" />
            <el-option label="按创建时间排序" value="time" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterBy" placeholder="筛选条件" @change="handleFilterChange">
            <el-option label="全部标签" value="all" />
            <el-option label="已使用标签" value="used" />
            <el-option label="未使用标签" value="unused" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <div class="view-controls">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="grid">
                <el-icon><Grid /></el-icon>
                卡片视图
              </el-radio-button>
              <el-radio-button label="grouped">
                <el-icon><CollectionTag /></el-icon>
                分组视图
              </el-radio-button>
            </el-radio-group>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 标签列表 -->
    <div class="labels-section">
      <div v-if="labelStore.loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>
      <div v-else-if="displayLabels.length === 0" class="empty-container">
        <el-empty description="暂无标签数据">
          <el-button type="primary" @click="showCreateDialog = true">
            创建第一个标签
          </el-button>
        </el-empty>
      </div>
      <div v-else>
        <!-- 卡片视图 -->
        <div v-if="viewMode === 'grid'" class="labels-grid">
          <LabelCard
            v-for="label in displayLabels"
            :key="label.id"
            :label="label"
            :stats="labelStore.getLabelStats(label.label)"
            :maxUsageCount="maxUsageCount"
            @delete="handleDeleteLabel"
            @edit="handleEditLabel"
          />
        </div>
        
        <!-- 分组视图 -->
        <div v-else-if="viewMode === 'grouped'" class="grouped-view">
          <div v-for="(group, groupName) in groupedLabels" :key="groupName" class="label-group">
            <div class="group-header">
              <div class="group-info">
                <el-icon class="group-icon"><FolderOpened /></el-icon>
                <span class="group-name">{{ groupName || '未分组' }}</span>
                <el-tag size="small" type="info">{{ group.length }}个标签</el-tag>
              </div>
              <div class="group-stats">
                <span class="group-usage">总使用: {{ getGroupUsageCount(group) }}次</span>
              </div>
            </div>
            <div class="group-labels">
              <LabelCard
                v-for="label in group"
                :key="label.id"
                :label="label"
                :stats="labelStore.getLabelStats(label.label)"
                :maxUsageCount="maxUsageCount"
                @delete="handleDeleteLabel"
                @edit="handleEditLabel"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 标签统计图表 -->
    <div v-if="labelStore.hasLabels" class="chart-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>标签使用统计</span>
            <div class="chart-controls">
              <el-select v-model="chartGroupFilter" size="small" placeholder="选择分组" style="width: 150px;">
                <el-option label="全部分组" value="" />
                <el-option 
                  v-for="group in availableGroups" 
                  :key="group" 
                  :label="group || '未分组'" 
                  :value="group || ''" 
                />
              </el-select>
            </div>
          </div>
        </template>
        <LabelStatsChart :stats="filteredChartStats" />
      </el-card>
    </div>

    <!-- 新增标签对话框 -->
    <CreateLabelDialog
      v-model="showCreateDialog"
      @created="handleLabelCreated"
    />

    <!-- 编辑标签对话框 -->
    <EditLabelDialog
      v-model="showEditDialog"
      :label="editingLabel"
      @updated="handleLabelUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search,
  Grid,
  CollectionTag,
  FolderOpened,
  ArrowUp,
  ArrowDown
} from '@element-plus/icons-vue'
import { useLabelStore } from '@/stores/label'
import PageHeader from '@/components/common/PageHeader.vue'
import LabelCard from '@/components/label/LabelCard.vue'
import LabelStatsChart from '@/components/label/LabelStatsChart.vue'
import CreateLabelDialog from '@/components/label/CreateLabelDialog.vue'
import EditLabelDialog from '@/components/label/EditLabelDialog.vue'
import ModernButton from '@/components/common/ModernButton.vue'
import type { LabelResponse } from '@/types/api'

const labelStore = useLabelStore()

// 响应式数据
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const editingLabel = ref<LabelResponse | null>(null)
const searchQuery = ref('')
const sortBy = ref('usage')
const filterBy = ref('all')
const selectedGroup = ref('')
const viewMode = ref('grid') // 'grid' | 'grouped'
const chartGroupFilter = ref('')
const showQuickCreate = ref(false)
const quickFormRef = ref()
const quickForm = ref({
  label: '',
  groups: ''
})
const quickRules = ref({
  label: [{ required: true, message: '请输入标签名称', trigger: 'blur' }]
})
const quickCreating = ref(false)

// 面包屑导航配置
const breadcrumbs = [
  { text: '标签管理' }
]

// 定义统计项类型
interface StatItem {
  key: string
  label: string
  value: string | number
  type?: 'total' | 'success' | 'warning' | 'primary' | 'info' | 'danger' | 'default'
  icon?: string
}

// 头部统计信息
const headerStats = computed<StatItem[]>(() => {
  if (labelStore.loading) return []
  
  return [
    {
      key: 'texts',
      label: '已标注文本',
      value: labelStore.statsOverview.labeledTexts,
      type: 'info',
      icon: 'fas fa-file-text'
    },
    {
      key: 'groups',
      label: '标签分组',
      value: availableGroups.value.length,
      type: 'primary',
      icon: 'fas fa-layer-group'
    },
    {
      key: 'unused',
      label: '未使用',
      value: labelStore.statsOverview.unusedLabels,
      type: 'warning',
      icon: 'fas fa-exclamation-triangle'
    },
    {
      key: 'used',
      label: '已使用',
      value: labelStore.statsOverview.usedLabels,
      type: 'success',
      icon: 'fas fa-check'
    },
    {
      key: 'total',
      label: '总标签数',
      value: labelStore.statsOverview.totalLabels,
      type: 'total',
      icon: 'fas fa-tags'
    }
  ]
})

// 获取所有可用的分组
const availableGroups = computed(() => {
  const groups = new Set<string>()
  labelStore.labels.forEach((label: LabelResponse) => {
    if (label.groups) {
      // 解析分组层级，例如 "NLP/意图/分类" 
      const groupParts = label.groups.split('/')
      for (let i = 1; i <= groupParts.length; i++) {
        groups.add(groupParts.slice(0, i).join('/'))
      }
    } else {
      groups.add('') // 未分组
    }
  })
  return Array.from(groups).sort()
})

// 计算属性
const displayLabels = computed(() => {
  let labels = labelStore.filteredLabels

  // 应用分组筛选
  if (selectedGroup.value !== '') {
    labels = labels.filter(label => {
      if (selectedGroup.value === '') {
        return !label.groups // 未分组
      }
      return label.groups && label.groups.startsWith(selectedGroup.value)
    })
  }

  // 应用筛选条件
  if (filterBy.value === 'used') {
    labels = labels.filter(label => {
      const stats = labelStore.getLabelStats(label.label)
      return stats && stats.count > 0
    })
  } else if (filterBy.value === 'unused') {
    labels = labels.filter(label => {
      const stats = labelStore.getLabelStats(label.label)
      return !stats || stats.count === 0
    })
  }

  // 应用排序
  if (sortBy.value === 'usage') {
    return [...labels].sort((a, b) => {
      const aCount = labelStore.getLabelStats(a.label)?.count || 0
      const bCount = labelStore.getLabelStats(b.label)?.count || 0
      return bCount - aCount
    })
  } else if (sortBy.value === 'name') {
    return [...labels].sort((a, b) => a.label.localeCompare(b.label))
  } else if (sortBy.value === 'group') {
    return [...labels].sort((a, b) => {
      const aGroup = a.groups || '未分组'
      const bGroup = b.groups || '未分组'
      if (aGroup === bGroup) {
        return a.label.localeCompare(b.label)
      }
      return aGroup.localeCompare(bGroup)
    })
  } else {
    // 按ID排序（近似创建时间）
    return [...labels].sort((a, b) => b.id - a.id)
  }
})

// 分组后的标签（用于分组视图）
const groupedLabels = computed(() => {
  const groups: Record<string, LabelResponse[]> = {}
  
  displayLabels.value.forEach(label => {
    const groupName = label.groups || ''
    if (!groups[groupName]) {
      groups[groupName] = []
    }
    groups[groupName].push(label)
  })
  
  return groups
})

// 计算所有标签中的最大使用次数，用于百分比计算
const maxUsageCount = computed(() => {
  if (!labelStore.hasLabels) return 0
  
  let maxCount = 0
  labelStore.labels.forEach((label: LabelResponse) => {
    const stats = labelStore.getLabelStats(label.label)
    if (stats && stats.count > maxCount) {
      maxCount = stats.count
    }
  })
  
  return maxCount
})

// 图表统计数据过滤
const filteredChartStats = computed(() => {
  const stats = labelStore.systemStats?.label_statistics || []
  if (!chartGroupFilter.value) return stats
  
  return stats.filter(stat => {
    const label = labelStore.labels.find(l => l.label === stat.label)
    if (!label) return false
    
    if (chartGroupFilter.value === '') {
      return !label.groups
    }
    return label.groups && label.groups.startsWith(chartGroupFilter.value)
  })
})

// 方法
const handleSearch = (value: string) => {
  // 扩展搜索功能，支持描述搜索
  labelStore.setSearchQuery(value)
}

const handleSortChange = () => {
  // 排序逻辑在计算属性中处理
}

const handleFilterChange = () => {
  // 筛选逻辑在计算属性中处理
}

const handleGroupFilter = () => {
  // 分组筛选逻辑在计算属性中处理
}

const handleLabelCreated = () => {
  ElMessage.success('标签创建成功')
  showCreateDialog.value = false
}

const handleEditLabel = (label: LabelResponse) => {
  editingLabel.value = label
  showEditDialog.value = true
}

const handleLabelUpdated = () => {
  ElMessage.success('标签更新成功')
  showEditDialog.value = false
  editingLabel.value = null
}

const handleDeleteLabel = async (label: LabelResponse) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${label.label}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await labelStore.deleteLabel(label.id)
    ElMessage.success('标签删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除标签失败')
    }
  }
}

// 获取分组的总使用次数
const getGroupUsageCount = (labels: LabelResponse[]) => {
  return labels.reduce((sum, label) => {
    const stats = labelStore.getLabelStats(label.label)
    return sum + (stats?.count || 0)
  }, 0)
}

const handleQuickCreate = async () => {
  if (!quickFormRef.value) return
  
  try {
    await quickFormRef.value.validate()
    quickCreating.value = true
    
    const labelData = {
      label: quickForm.value.label.trim(),
      description: null,
      groups: quickForm.value.groups?.trim() || null
    }
    
    await labelStore.createLabel(labelData)
    ElMessage.success('标签创建成功')
    resetQuickForm()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('创建标签失败')
    }
  } finally {
    quickCreating.value = false
  }
}

const resetQuickForm = () => {
  quickForm.value = {
    label: '',
    groups: ''
  }
  quickFormRef.value?.clearValidate()
}

// 生命周期
onMounted(async () => {
  try {
    await labelStore.initializeData()
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
})
</script>

<style scoped>
.label-manage-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.search-section,
.labels-section,
.chart-section {
  padding: 0 16px;
  margin-bottom: 16px;
}

.search-section {
  margin-top: 0;
}

.view-controls {
  display: flex;
  justify-content: flex-end;
}

.loading-container,
.empty-container {
  background: white;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
}

.labels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  min-height: 0;
  max-height: 60vh;
  overflow: auto;
}

.grouped-view {
  max-height: 60vh;
  overflow: auto;
}

.label-group {
  margin-bottom: 24px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e9ecef;
}

.group-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-icon {
  color: #6c757d;
  font-size: 16px;
}

.group-name {
  font-weight: 600;
  color: #495057;
  font-size: 16px;
}

.group-stats {
  font-size: 13px;
  color: #6c757d;
}

.group-labels {
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.create-btn-section {
  padding: 0 16px;
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.create-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.quick-create-form {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
}

  @media (max-width: 768px) {
    .labels-grid,
    .group-labels {
      grid-template-columns: 1fr;
    }
    
    .search-section,
    .labels-section,
    .chart-section {
      padding: 0 8px;
    }
    
    .search-section .el-row {
      flex-direction: column;
      gap: 12px;
    }
    
    .search-section .el-col {
      width: 100%;
    }
    
    .view-controls {
      justify-content: center;
    }
    
    .create-actions {
      flex-direction: column;
      align-items: stretch;
    }
    
    .quick-create-form :deep(.el-form--inline) {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .quick-create-form :deep(.el-form-item) {
      margin-right: 0 !important;
    }
  }
</style> 