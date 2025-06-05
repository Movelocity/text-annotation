# 标签筛选功能优化

## 概述
将FilterPanel和BatchActions组件中的标签筛选功能从手动输入改为从全局store选择，提升用户体验和数据一致性。

## 主要变更

### 1. FilterPanel.vue 组件优化
- **原有方式**: 使用 `el-input` 手动输入标签名称
- **优化后**: 使用 `el-select` 从标签store选择已存在的标签
- **优势**: 
  - 避免标签名称拼写错误
  - 确保筛选使用的是系统中真实存在的标签
  - 提供标签自动完成和搜索功能

#### 技术实现
```typescript
// 导入标签store
import { useLabelStore } from '@/stores/label'

// 可用标签选项（排除已选择的）
const availableLabelOptions = computed(() => {
  return labelStore.labelOptions.filter(option => 
    !props.includeLabels.includes(option.value) && 
    !props.excludeLabels.includes(option.value)
  )
})

// 组件挂载时初始化标签数据
onMounted(async () => {
  if (!labelStore.hasLabels) {
    await labelStore.fetchLabels()
  }
})
```

### 2. BatchActions.vue 组件优化
- **原有方式**: 使用 `el-input` 手动输入要添加/删除的标签
- **优化后**: 使用 `el-select` 从标签store选择标签
- **优势**:
  - 批量操作时确保标签的准确性
  - 提供已有标签的可视化选择
  - 避免创建无效或重复标签

## 用户体验改进

### 筛选操作
1. **智能标签选择**: 下拉列表自动排除已选择的标签，避免重复添加
2. **搜索功能**: 支持在标签列表中快速搜索
3. **清空功能**: 提供快速清空选择的功能

### 批量操作
1. **标签一致性**: 确保批量添加的标签都是系统中存在的
2. **操作反馈**: 选择标签后立即显示在界面上
3. **错误减少**: 杜绝因手动输入导致的标签名称错误

## 数据流
```
用户操作 → 标签Store → 组件选项 → 筛选/批量操作 → API调用
```

## 测试建议
1. **功能测试**: 验证标签选择功能正常工作
2. **数据一致性**: 确保选择的标签与store中的数据一致
3. **错误处理**: 测试网络错误或数据加载失败的情况
4. **用户体验**: 验证下拉选择比手动输入更高效

## 注意事项
- 组件首次加载时会自动获取标签数据
- 标签数据通过store统一管理，确保组件间的数据一致性
- 支持标签的实时搜索和过滤功能
- 已选择的标签会从可选列表中自动移除，避免重复选择

## 后续优化建议
1. 添加标签使用频率显示
2. 支持标签分组或分类显示
3. 提供最近使用标签的快速选择
4. 考虑添加新标签的快捷入口（如果需要） 