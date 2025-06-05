<template>
  <div class="label-manage-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Collection /></el-icon>
          标签管理
        </h1>
        <p class="page-description">管理和查看所有标签的使用情况</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          @click="showCreateDialog = true"
          :loading="labelStore.loading"
        >
          <el-icon><Plus /></el-icon>
          新增标签
        </el-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon total">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ labelStore.statsOverview.totalLabels }}</div>
                <div class="stats-label">总标签数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon used">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ labelStore.statsOverview.usedLabels }}</div>
                <div class="stats-label">已使用标签</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon unused">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ labelStore.statsOverview.unusedLabels }}</div>
                <div class="stats-label">未使用标签</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon texts">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ labelStore.statsOverview.labeledTexts }}</div>
                <div class="stats-label">已标注文本</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

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
  Collection, 
  Plus, 
  Check, 
  Warning, 
  Document, 
  Search 
} from '@element-plus/icons-vue'
import { useLabelStore } from '@/stores/label'
import LabelCard from '@/components/label/LabelCard.vue'
import LabelStatsChart from '@/components/label/LabelStatsChart.vue'
import CreateLabelDialog from '@/components/label/CreateLabelDialog.vue'
import type { LabelResponse } from '@/types/api'

const labelStore = useLabelStore()

// 响应式数据
const showCreateDialog = ref(false)
const searchQuery = ref('')
const sortBy = ref('usage')
const filterBy = ref('all')

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
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  flex-shrink: 0;
}

.stats-overview {
  margin-bottom: 24px;
}

.stats-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stats-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.used {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.unused {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #e6a23c;
}

.stats-icon.texts {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #409eff;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.search-section {
  margin-bottom: 24px;
}

.labels-section {
  margin-bottom: 24px;
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

.chart-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .labels-grid {
    grid-template-columns: 1fr;
  }
}
</style> 