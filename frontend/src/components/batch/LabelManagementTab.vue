<!--
  标签管理Tab组件
  功能：展示所有标签、统计信息、支持分组展示和编辑
-->
<template>
  <div class="label-management-tab">
    <!-- 搜索和工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索标签..."
        size="medium"
        clearable
        prefix-icon="Search"
        class="search-input"
        @input="clearHighlight"
      />
      <div class="toolbar-actions">
        <el-button
          size="small"
          :type="showGrouped ? 'primary' : 'default'"
          @click="showGrouped = !showGrouped"
        >
          <i class="fas fa-layer-group"></i>
          分组显示
        </el-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview" v-if="labelStore.statsOverview">
      <div class="stat-item">
        <span class="stat-label">总标签</span>
        <span class="stat-value">{{ labelStore.statsOverview.totalLabels }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">已使用</span>
        <span class="stat-value success">{{ labelStore.statsOverview.usedLabels }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">未使用</span>
        <span class="stat-value warning">{{ labelStore.statsOverview.unusedLabels }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总数据</span>
        <span class="stat-value">{{ labelStore.statsOverview.totalTexts }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">已标注</span>
        <span class="stat-value success">{{ labelStore.statsOverview.labeledTexts }}</span>
      </div>
    </div>

    <!-- 标签列表 -->
    <div class="labels-container" v-loading="labelStore.loading" @click="clearHighlight">
      <!-- 分组显示 -->
      <div v-if="showGrouped" class="grouped-labels">
        <div
          v-for="group in groupedLabels"
          :key="group.name"
          class="label-group"
        >
          <div 
            class="group-header"
            @click="toggleGroupCollapse(group.name)"
          >
            <i :class="['fas', group.collapsed ? 'fa-chevron-right' : 'fa-chevron-down']"></i>
            <span class="group-name">{{ group.name }}</span>
            <span class="group-count">({{ group.labels.length }})</span>
            <el-button
              v-if="group.name !== '未分组'"
              size="small"
              text
              type="primary"
              @click.stop="editGroupName(group.name)"
            >
              <i class="fas fa-edit"></i>
            </el-button>
          </div>
          <div v-show="!group.collapsed" class="group-content">
            <LabelItem
              v-for="label in group.labels"
              :key="label.id"
              :label="label"
              :stats="labelStore.getLabelStats(label.label)"
              :max-usage-count="maxUsageCount"
              :is-highlighted="highlightedLabels.has(label.label)"
              @click="handleLabelClick"
              @edit="handleLabelEdit"
              @filter="handleLabelFilter"
            />
          </div>
        </div>
      </div>

      <!-- 列表显示 -->
      <div v-else class="flat-labels">
        <LabelItem
          v-for="label in filteredLabels"
          :key="label.id"
          :label="label"
          :stats="labelStore.getLabelStats(label.label)"
          :max-usage-count="maxUsageCount"
          :is-highlighted="highlightedLabels.has(label.label)"
          @click="handleLabelClick"
          @edit="handleLabelEdit"
          @filter="handleLabelFilter"
        />
      </div>
    </div>

    <!-- 编辑分组名称对话框 -->
    <el-dialog
      v-model="editGroupDialog.show"
      title="编辑分组名称"
      width="400px"
    >
      <el-form>
        <el-form-item label="分组名称">
          <el-input
            v-model="editGroupDialog.newName"
            placeholder="输入新的分组名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editGroupDialog.show = false">取消</el-button>
        <el-button type="primary" @click="saveGroupName">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useLabelStore } from '@/stores/label'
import LabelItem from './LabelItem.vue'
import type { LabelResponse, LabelUpdate } from '@/types/api'

// Props & Emits
interface Emits {
  'label-selected': [label: string]
  'label-filtered': [label: string]
}

const emit = defineEmits<Emits>()

// Store
const labelStore = useLabelStore()

// 响应式状态
const searchQuery = ref('')
const showGrouped = ref(true)
const collapsedGroups = ref<Set<string>>(new Set())
const highlightedLabels = ref<Set<string>>(new Set())

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

// 方法
const clearHighlight = () => {
  highlightedLabels.value.clear()
}

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

const saveGroupName = async () => {
  const { oldName, newName } = editGroupDialog.value
  
  if (!newName.trim() || oldName === newName) {
    editGroupDialog.value.show = false
    return
  }

  try {
    // 更新该分组下所有标签的分组名称
    const labelsToUpdate = filteredLabels.value.filter(
      label => (label.groups || '未分组') === oldName
    )

    for (const label of labelsToUpdate) {
      const updateData: LabelUpdate = {
        label: label.label,
        description: label.description,
        groups: newName === '未分组' ? null : newName
      }
      await labelStore.updateLabel(label.id, updateData)
    }

    ElMessage.success('分组名称更新成功')
    editGroupDialog.value.show = false
  } catch (error) {
    ElMessage.error('更新分组名称失败')
    console.error('Error updating group name:', error)
  }
}

const handleLabelClick = (label: LabelResponse) => {
  const labelName = label.label
  
  // 清除所有之前的高亮，只保持当前选中的标签高亮
  highlightedLabels.value.clear()
  highlightedLabels.value.add(labelName)
  
  emit('label-selected', labelName)
}

const handleLabelEdit = async (label: LabelResponse, updates: Partial<LabelUpdate>) => {
  try {
    // 构建完整的更新数据
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

const handleLabelFilter = (labelName: string) => {
  // 清除所有之前的高亮，只保持当前选中的标签高亮
  highlightedLabels.value.clear()
  highlightedLabels.value.add(labelName)
  
  // 触发过滤事件
  emit('label-filtered', labelName)
}

// 生命周期
onMounted(async () => {
  if (!labelStore.hasLabels) {
    await labelStore.fetchLabels()
  }
  
  if (!labelStore.systemStats) {
    await labelStore.fetchSystemStats()
  }
})

onUnmounted(() => {
  // 清理高亮状态
  highlightedLabels.value.clear()
})
</script>

<style scoped>
.label-management-tab {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  height: 100%;
}

.toolbar {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.search-input {
  flex: 1;
}

.toolbar-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.stats-overview {
  display: flex;
  justify-content: space-around;
  gap: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--el-fill-color-extra-light);
  border-radius: var(--el-border-radius-base);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stat-value.success {
  color: var(--el-color-success);
}

.stat-value.warning {
  color: var(--el-color-warning);
}

.labels-container {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.label-group {
  margin-bottom: var(--spacing-md);
}

.group-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.group-header:hover {
  background: var(--el-fill-color);
}

.group-name {
  flex: 1;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.group-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.group-content {
  margin-top: var(--spacing-sm);
  padding-left: var(--spacing-lg);
}

.flat-labels {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
</style> 