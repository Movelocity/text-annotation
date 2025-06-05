<template>
  <div class="label-manage-page">
    <!-- 页面头部 -->
    <PageHeader
      title="标签管理"
      title-icon="fas fa-tags"
      :breadcrumbs="breadcrumbs"
      :stats="headerStats"
      home-route="/home"
    >
      <template #actions>
        <ModernButton
          text="新增标签"
          icon="fas fa-plus"
          type="primary"
          :loading="labelStore.loading"
          @click="showCreateDialog = true"
        />
      </template>
    </PageHeader>

    <!-- 搜索和过滤 -->
    <div class="search-section">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索标签名称..."
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="8">
          <el-select v-model="sortBy" placeholder="排序方式" @change="handleSortChange">
            <el-option label="按使用频率排序" value="usage" />
            <el-option label="按名称排序" value="name" />
            <el-option label="按创建时间排序" value="time" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select v-model="filterBy" placeholder="筛选条件" @change="handleFilterChange">
            <el-option label="全部标签" value="all" />
            <el-option label="已使用标签" value="used" />
            <el-option label="未使用标签" value="unused" />
          </el-select>
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
      <div v-else class="labels-grid">
        <LabelCard
          v-for="label in displayLabels"
          :key="label.id"
          :label="label"
          :stats="labelStore.getLabelStats(label.label)"
          :maxUsageCount="maxUsageCount"
          @delete="handleDeleteLabel"
        />
      </div>
    </div>

    <!-- 标签统计图表 -->
    <div v-if="labelStore.hasLabels" class="chart-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>标签使用统计</span>
          </div>
        </template>
        <LabelStatsChart :stats="labelStore.systemStats?.label_statistics || []" />
      </el-card>
    </div>

    <!-- 新增标签对话框 -->
    <CreateLabelDialog
      v-model="showCreateDialog"
      @created="handleLabelCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search 
} from '@element-plus/icons-vue'
import { useLabelStore } from '@/stores/label'
import PageHeader from '@/components/common/PageHeader.vue'
import LabelCard from '@/components/label/LabelCard.vue'
import LabelStatsChart from '@/components/label/LabelStatsChart.vue'
import CreateLabelDialog from '@/components/label/CreateLabelDialog.vue'
import ModernButton from '@/components/common/ModernButton.vue'
import type { LabelResponse } from '@/types/api'

const labelStore = useLabelStore()

// 响应式数据
const showCreateDialog = ref(false)
const searchQuery = ref('')
const sortBy = ref('usage')
const filterBy = ref('all')

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
      key: 'total',
      label: '总标签数',
      value: labelStore.statsOverview.totalLabels,
      type: 'total',
      icon: 'fas fa-tags'
    },
    {
      key: 'used',
      label: '已使用',
      value: labelStore.statsOverview.usedLabels,
      type: 'success',
      icon: 'fas fa-check'
    },
    {
      key: 'unused',
      label: '未使用',
      value: labelStore.statsOverview.unusedLabels,
      type: 'warning',
      icon: 'fas fa-exclamation-triangle'
    },
    {
      key: 'texts',
      label: '已标注文本',
      value: labelStore.statsOverview.labeledTexts,
      type: 'info',
      icon: 'fas fa-file-text'
    }
  ]
})

// 计算属性
const displayLabels = computed(() => {
  let labels = labelStore.filteredLabels

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
  } else {
    // 按ID排序（近似创建时间）
    return [...labels].sort((a, b) => b.id - a.id)
  }
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

// 方法
const handleSearch = (value: string) => {
  labelStore.setSearchQuery(value)
}

const handleSortChange = () => {
  // 排序逻辑在计算属性中处理
}

const handleFilterChange = () => {
  // 筛选逻辑在计算属性中处理
}

const handleLabelCreated = () => {
  ElMessage.success('标签创建成功')
  showCreateDialog.value = false
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
}



.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

@media (max-width: 768px) {
  .labels-grid {
    grid-template-columns: 1fr;
  }
  
  .search-section,
  .labels-section,
  .chart-section {
    padding: 0 8px;
  }
}
</style> 