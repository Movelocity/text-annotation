<!--
  标签管理Tab组件
  功能：展示所有标签、统计信息、支持分组展示和编辑
-->
<template>
  <div class="label-management-tab">
    <!-- 工具栏 -->
    <div class="toolbar">
      <!-- 搜索框 -->
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索标签名称、描述或分组..."
          :prefix-icon="Search"
          clearable
          class="search-input"
        />
      </div>

      <!-- 右侧工具 -->
      <div class="toolbar-right">
        <!-- 显示模式切换 -->
        <el-button :type="showGrouped? 'primary' : 'default'" @click="showGrouped = !showGrouped" size="small">
          {{ showGrouped ? '切换平铺' : '切换分组' }}
        </el-button>
         
        <!-- <el-switch v-model="showGrouped" /> -->
        

        <!-- 当前筛选状态 -->
        <!-- <div v-if="selectedLabel" class="current-filter">
          <el-tag
            type="primary"
            closable
            @close="emit('label-selected', '')"
          >
            已筛选: {{ selectedLabel }}
          </el-tag>
        </div> -->
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stats-content">
        <div class="stat-item">
          <span class="stat-label">总标签数:</span>
          <span class="stat-value">{{ labelStore.labels.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">已使用:</span>
          <span class="stat-value">{{ labelStore.statsOverview.usedLabels }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">未使用:</span>
          <span class="stat-value">{{ labelStore.statsOverview.unusedLabels }}</span>
        </div>
        <div class="stat-item" v-if="searchQuery">
          <span class="stat-label">搜索结果:</span>
          <span class="stat-value">{{ filteredLabels.length }}</span>
        </div>
      </div>
    </div>

    <!-- 标签列表 -->
    <div class="labels-container">
      <!-- 分组显示 -->
      <template v-if="showGrouped">
        <div v-for="group in groupedLabels" :key="group.name" class="label-group">
          <!-- 分组头部 -->
          <div class="group-header" @click="toggleGroupCollapse(group.name)">
            <div class="group-title">
              <el-icon class="collapse-icon" :class="{ 'collapsed': group.collapsed }">
                <ArrowDown />
              </el-icon>
              <span class="group-name">{{ group.name }}</span>
              <el-tag size="small" type="info" class="group-count">
                {{ group.labels.length }}
              </el-tag>
            </div>
            <div class="group-actions">
              <el-button
                v-if="group.name !== '未分组'"
                size="small"
                link
                @click.stop="editGroupName(group.name)"
              >
                重命名
              </el-button>
            </div>
          </div>

          <!-- 分组内容 -->
          <el-collapse-transition>
            <div v-show="!group.collapsed" class="group-content">
              <div class="label-grid">
                <LabelItem
                   v-for="label in group.labels"
                   :key="label.id"
                   :label="label"
                   :is-highlighted="selectedLabel === label.label"
                   :stats="labelStore.getLabelStats(label.label)"
                   :max-usage-count="maxUsageCount"
                   @click="handleLabelSelect"
                   @edit="handleLabelEdit"
                />
              </div>
            </div>
          </el-collapse-transition>
        </div>
      </template>

      <!-- 平铺显示 -->
      <template v-else>
        <div class="label-grid">
                     <LabelItem
             v-for="label in filteredLabels"
             :key="label.id"
             :label="label"
             :is-highlighted="selectedLabel === label.label"
             :stats="labelStore.getLabelStats(label.label)"
             :max-usage-count="maxUsageCount"
             @click="handleLabelSelect"
             @edit="handleLabelEdit"
           />
        </div>
      </template>

      <!-- 空状态 -->
      <div v-if="filteredLabels.length === 0" class="empty-state">
        <el-empty description="暂无标签数据">
          <template #image>
            <el-icon size="64" color="#c0c4cc">
              <Document />
            </el-icon>
          </template>
        </el-empty>
      </div>
    </div>

    <!-- 编辑分组对话框 -->
    <el-dialog
      v-model="editGroupDialog.show"
      title="重命名分组"
      width="400px"
      :before-close="() => editGroupDialog.show = false"
    >
      <el-form @submit.prevent>
        <el-form-item label="分组名称">
          <el-input
            v-model="editGroupDialog.newName"
            placeholder="请输入新的分组名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editGroupDialog.show = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!editGroupDialog.newName.trim() || editGroupDialog.newName === editGroupDialog.oldName"
          @click="handleGroupRename"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, ArrowDown, Document } from '@element-plus/icons-vue'
import { useLabelStore } from '@/stores/label'
import LabelItem from './LabelItem.vue'
import type { LabelResponse, LabelUpdate } from '@/types/api'

// Props & Emits
interface Props {
  currentFilterLabel?: string | null
}

interface Emits {
  'label-selected': [label: string]
}

const props = withDefaults(defineProps<Props>(), {
  currentFilterLabel: null
})

const emit = defineEmits<Emits>()

// Store
const labelStore = useLabelStore()

// 响应式状态
const searchQuery = ref('')
const showGrouped = ref(true)
const collapsedGroups = ref<Set<string>>(new Set())

// 计算当前选中的标签，基于外部传入的筛选状态
const selectedLabel = computed(() => props.currentFilterLabel)

// 编辑分组对话框状态
const editGroupDialog = ref({
  show: false,
  oldName: '',
  newName: ''
})

// 计算属性
const filteredLabels = computed(() => {
  if (!searchQuery.value.trim()) {
    return labelStore.labelsByUsage
  }
  const query = searchQuery.value.toLowerCase()
  return labelStore.labelsByUsage.filter(label => 
    label.label.toLowerCase().includes(query) ||
    (label.description && label.description.toLowerCase().includes(query)) ||
    (label.groups && label.groups.toLowerCase().includes(query))
  )
})

const groupedLabels = computed(() => {
  const groups: Record<string, LabelResponse[]> = {}
  
  filteredLabels.value.forEach(label => {
    const groupName = label.groups || '未分组'
    if (!groups[groupName]) {
      groups[groupName] = []
    }
    groups[groupName].push(label)
  })

  return Object.entries(groups)
    .sort(([a], [b]) => {
      // 未分组放在最后
      if (a === '未分组') return 1
      if (b === '未分组') return -1
      return a.localeCompare(b)
    })
    .map(([name, labels]) => ({
      name,
      labels,
      collapsed: collapsedGroups.value.has(name)
    }))
})

const maxUsageCount = computed(() => {
  return Math.max(
    ...labelStore.labels.map(label => {
      const stats = labelStore.getLabelStats(label.label)
      return stats?.count ?? 0
    }),
    1
  )
})


const toggleGroupCollapse = (groupName: string) => {
  if (collapsedGroups.value.has(groupName)) {
    collapsedGroups.value.delete(groupName)
  } else {
    collapsedGroups.value.add(groupName)
  }
}

const editGroupName = (oldName: string) => {
  editGroupDialog.value = {
    show: true,
    oldName,
    newName: oldName
  }
}

const handleGroupRename = async () => {
  try {
    const { oldName, newName } = editGroupDialog.value
    if (!newName.trim() || newName === oldName) {
      return
    }

    // 更新所有属于这个分组的标签
    const labelsToUpdate = labelStore.labels.filter(label => label.groups === oldName)
    
    for (const label of labelsToUpdate) {
      await labelStore.updateLabel(label.id, {
        label: label.label,
        description: label.description,
        groups: newName.trim()
      })
    }

    ElMessage.success(`分组已重命名为: ${newName}`)
    editGroupDialog.value.show = false
  } catch (error) {
    ElMessage.error('重命名分组失败')
    console.error('Error renaming group:', error)
  }
}

const handleLabelSelect = (label: LabelResponse) => {
  const labelName = label.label
  
  // 总是触发选择事件，让父组件决定是选中还是取消选中
  emit('label-selected', labelName)
}

const handleLabelEdit = async (label: LabelResponse, updates: Partial<LabelUpdate>) => {
  try {
    const fullUpdateData: LabelUpdate = {
      label: updates.label || label.label,
      description: updates.description !== undefined ? updates.description : label.description,
      groups: updates.groups !== undefined ? updates.groups : label.groups
    }
    await labelStore.updateLabel(label.id, fullUpdateData)
    ElMessage.success('标签更新成功')
  } catch (error) {
    ElMessage.error('更新标签失败')
    console.error('Error updating label:', error)
  }
}

// 生命周期
onMounted(async () => {
  if (!labelStore.systemStats) {
    await labelStore.fetchSystemStats()
  }
})

onUnmounted(() => {
  // 清理工作由父组件处理
})
</script>

<style scoped>
.label-management-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 工具栏 */
.toolbar {
  padding: 8px 12px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.search-section {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.current-filter {
  white-space: nowrap;
}

/* 统计信息 */
.stats-bar {
  padding: 6px 12px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.stats-card {
  border: none;
  background: transparent;
}

.stats-content {
  display: flex;
  gap: 24px;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #606266;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

/* 标签容器 */
.labels-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
}

/* 分组显示 */
.label-group {
  margin-bottom: 8px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.group-header:hover {
  background: #e9ecef;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-icon {
  transition: transform 0.2s;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.group-name {
  font-weight: 500;
  color: #303133;
}

.group-count {
  margin-left: 4px;
}

.group-actions {
  display: flex;
  gap: 8px;
}

.group-content {
  margin-top: 8px;
}

/* 标签网格 */
.label-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 8px;
}

@media (max-width: 768px) {
  .label-grid {
    grid-template-columns: 1fr;
  }
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #909399;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-right {
    justify-content: space-between;
  }
  
  .stats-content {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .search-section {
    max-width: none;
  }
}
</style> 