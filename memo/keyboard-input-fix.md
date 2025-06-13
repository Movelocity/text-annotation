# 键盘输入拦截问题修复

## 问题描述
- **现象**: 文本列表搜索框无法输入空格和数字
- **影响范围**: 所有输入框（搜索框、标签选择框等）
- **原因**: 全局快捷键监听器拦截了键盘输入

## 问题根源
在 `LabelSelector.vue` 组件中，注册了全局的键盘事件监听器：
- 监听数字键 1-9 用于快速选择标签
- 监听空格键用于跳过标注
- 监听 Enter 键用于保存
- **问题**: 使用 `document.addEventListener` 全局监听，影响所有输入框

## 解决方案
在快捷键处理函数中添加输入框检测逻辑：

```typescript
const handleKeyDown = (event: KeyboardEvent) => {
  // 检查是否在输入框或可编辑元素中
  const target = event.target as HTMLElement
  const isInputElement = target && (
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.isContentEditable ||
    target.closest('.el-input__wrapper') ||
    target.closest('.el-select') ||
    target.closest('.el-textarea')
  )

  // 如果在输入框中，不处理快捷键
  if (isInputElement) {
    return
  }
  
  // 后续快捷键处理...
}
```

## 修复范围
1. **LabelSelector.vue**: 修复数字键和空格键拦截
2. **FilterConditionsTab.vue**: 优化 Ctrl+Enter 处理

## 测试验证
- ✅ 搜索框可以正常输入空格
- ✅ 搜索框可以正常输入数字
- ✅ 标签选择框正常工作
- ✅ 快捷键在非输入框时正常工作

## 最佳实践
1. 全局快捷键监听应检测焦点元素类型
2. 避免在输入框获得焦点时拦截键盘输入
3. 使用 `closest()` 检测 Element Plus 组件包装器
4. 保持快捷键功能的同时确保输入体验 