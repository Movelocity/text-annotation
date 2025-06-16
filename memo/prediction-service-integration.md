# 预测服务集成开发记录

## 概述
为前端添加了意图预测服务调用功能，支持在AppHeader中配置预测服务地址，并提供测试组件。

## 新增文件

### 1. 预测服务 (`web/src/services/prediction.ts`)
- 实现意图预测API调用
- 支持配置管理（保存到localStorage）
- 提供连接测试功能
- 默认配置：`http://localhost:5000/v1/predict`

### 2. 配置弹窗组件 (`web/src/components/PredictionConfigDialog.vue`)
- 图形界面配置预测服务地址
- 实时显示完整URL
- 支持连接测试
- 支持重置到默认配置

### 3. 测试组件 (`web/src/components/PredictionTest.vue`)
- 提供意图预测测试界面
- 显示详细预测结果和置信度
- 支持快捷键操作（Ctrl+Enter）

## 修改文件

### AppHeader.vue
- 在用户下拉菜单中添加"预测服务配置"选项
- 集成配置弹窗组件
- 添加相关图标和样式

## API接口格式

### 请求
```typescript
POST /v1/predict
{
  "query": "Once my package is dispatched, will tracking details and the shipping carrier be accessible directly on the order information page?"
}
```

### 响应
```typescript
{
  "intent": "realTimeTrackingQuery",
  "prob": 0.7030657529830933,
  "query": "Once my package is dispatched, will tracking details and the shipping carrier be accessible directly on the order information page?",
  "result_dict": {
    "realTimeTrackingQuery": 0.7030657529830933
  },
  "status": 200
}
```

## 功能特性

1. **配置管理**: 服务地址保存在localStorage，支持持久化
2. **连接测试**: 配置前可测试连接可用性
3. **错误处理**: 完整的错误提示和处理机制
4. **用户体验**: 
   - 美观的UI界面
   - 实时反馈
   - 快捷键支持
   - 置信度可视化

## 使用方式

1. 点击AppHeader右上角用户头像
2. 选择"预测服务配置"
3. 配置预测服务地址（默认localhost:5000）
4. 测试连接并保存
5. 在代码中使用 `predictionService.predict(query)` 调用

## 技术栈
- Vue 3 + TypeScript
- Element Plus UI组件
- Axios HTTP客户端
- LocalStorage持久化

## 待扩展功能
- 批量预测
- 预测历史记录
- 更多预测服务支持
- 预测结果导出 