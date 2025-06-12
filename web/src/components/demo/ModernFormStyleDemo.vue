<template>
  <div class="modern-form-demo">
    <div class="demo-header">
      <h3><i class="fas fa-palette"></i> 现代化表单样式演示</h3>
      <p>本组件展示项目中使用的现代化表单设计风格，供开发时参考。</p>
    </div>

    <!-- 现代化表单容器样式演示 -->
    <div class="modern-form-container">
      <div class="form-header">
        <div class="header-left">
          <i class="fas fa-bolt"></i>
          <span class="header-title">现代化表单示例</span>
          <el-tag type="success" size="small">设计指导</el-tag>
        </div>
        <div class="header-right">
          <el-button 
            link 
            class="reset-btn"
          >
            <i class="fas fa-refresh"></i> 重置
          </el-button>
        </div>
      </div>
      
      <div class="form-content">
        <el-form class="modern-form">
          <div class="form-row">
            <div class="form-group primary">
              <el-form-item class="label-input">
                <template #label>
                  <div class="input-label">
                    <i class="fas fa-tag"></i>
                    <span>主要输入字段</span>
                    <span class="required">*</span>
                  </div>
                </template>
                <el-input
                  placeholder="输入主要内容..."
                  :maxlength="50"
                  show-word-limit
                  clearable
                  size="large"
                  class="modern-input"
                >
                  <template #prefix>
                    <i class="fas fa-tag input-icon"></i>
                  </template>
                </el-input>
              </el-form-item>
            </div>
            
            <div class="form-group secondary">
              <el-form-item class="group-input">
                <template #label>
                  <div class="input-label">
                    <i class="fas fa-folder"></i>
                    <span>选择字段</span>
                    <span class="optional">(可选)</span>
                  </div>
                </template>
                <el-select
                  placeholder="选择或创建选项..."
                  filterable
                  allow-create
                  clearable
                  size="large"
                  class="modern-select"
                >
                  <template #prefix>
                    <i class="fas fa-folder input-icon"></i>
                  </template>
                  <el-option label="选项1" value="option1">
                    <div class="group-option">
                      <i class="fas fa-folder-open"></i>
                      <span>选项1</span>
                    </div>
                  </el-option>
                  <el-option label="选项2" value="option2">
                    <div class="group-option">
                      <i class="fas fa-folder-open"></i>
                      <span>选项2</span>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
            </div>
          </div>
          
          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large"
              class="create-btn"
            >
              <i class="fas fa-plus"></i>
              主要操作
            </el-button>
            <el-button 
              size="large"
              class="advanced-btn"
            >
              <i class="fas fa-cog"></i>
              次要操作
            </el-button>
          </div>
          
          <!-- 快捷键提示 -->
          <div class="shortcuts-hint">
            <el-tag type="info" size="small">
              <i class="fas fa-keyboard"></i> Enter 确认
            </el-tag>
            <el-tag type="info" size="small">
              <i class="fas fa-keyboard"></i> Esc 关闭
            </el-tag>
          </div>
        </el-form>
      </div>
      
      <!-- 最近项目演示 -->
      <div class="recent-labels">
        <div class="recent-header">
          <i class="fas fa-clock"></i>
          <span>最近项目</span>
        </div>
        <div class="recent-list">
          <el-tag class="recent-tag">
            示例标签1
            <span class="tag-group">
              <i class="fas fa-folder"></i>
              分组A
            </span>
          </el-tag>
          <el-tag class="recent-tag">
            示例标签2
            <span class="tag-group">
              <i class="fas fa-folder"></i>
              分组B
            </span>
          </el-tag>
          <el-tag class="recent-tag">
            示例标签3
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 设计说明 -->
    <div class="design-notes">
      <h4><i class="fas fa-lightbulb"></i> 设计要点</h4>
      <ul>
        <li><strong>渐变背景：</strong> 使用线性渐变创造层次感和现代感</li>
        <li><strong>圆角设计：</strong> 8-16px 圆角，营造友好的视觉效果</li>
        <li><strong>阴影层次：</strong> 多层阴影创造浮动效果</li>
        <li><strong>交互反馈：</strong> hover 和 focus 状态的平滑过渡</li>
        <li><strong>色彩搭配：</strong> 主色调 #409eff，辅助色彩丰富视觉层次</li>
        <li><strong>动画效果：</strong> 适度的变换和光效增强用户体验</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
// 这是一个样式演示组件，不包含具体的业务逻辑
// 主要用于展示现代化表单的设计风格
</script>

<style scoped>
.modern-form-demo {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.demo-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.demo-header h3 {
  margin: 0 0 12px 0;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.demo-header p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

.modern-form-container {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 16px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(64, 158, 255, 0.1);
  padding: 24px;
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
}

.modern-form-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 50%, #e6a23c 100%);
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(64, 158, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left i {
  color: #f39c12;
  font-size: 18px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.header-title {
  font-weight: 700;
  color: #2c3e50;
  font-size: 18px;
  letter-spacing: -0.5px;
}

.reset-btn {
  color: #6c757d;
  transition: all 0.3s ease;
}

.form-content {
  margin-bottom: 20px;
}

.modern-form .form-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  position: relative;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.required {
  color: #e74c3c;
  font-weight: 700;
}

.optional {
  color: #95a5a6;
  font-size: 12px;
  font-weight: 400;
}

.modern-input,
.modern-select {
  transition: all 0.3s ease;
}

.modern-input:deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  background: white;
}

.modern-input:deep(.el-input__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
}

.modern-input:deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.modern-select:deep(.el-select__wrapper) {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  background: white;
}

.modern-select:deep(.el-select__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
}

.modern-select:deep(.el-select__wrapper.is-focused) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.input-icon {
  color: #95a5a6;
  transition: color 0.3s ease;
}

.modern-input:deep(.el-input__wrapper.is-focus) .input-icon,
.modern-select:deep(.el-select__wrapper.is-focused) .input-icon {
  color: #409eff;
}

.group-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.create-btn {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  border: none;
  color: white;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.create-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.create-btn:hover::before {
  left: 100%;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.3);
}

.advanced-btn {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  color: #495057;
  font-weight: 500;
  padding: 12px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.advanced-btn:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.shortcuts-hint {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #dee2e6;
}

.shortcuts-hint .el-tag {
  background: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.2);
  color: #409eff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 6px;
}

.recent-labels {
  background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.recent-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.recent-header i {
  color: #3498db;
}

.recent-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recent-tag {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border: 1px solid rgba(64, 158, 255, 0.2);
  color: #2c3e50;
  padding: 6px 12px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.recent-tag:hover {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.tag-group {
  opacity: 0.7;
  font-size: 10px;
}

.tag-group i {
  font-size: 8px;
}

.design-notes {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.design-notes h4 {
  margin: 0 0 16px 0;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.design-notes ul {
  margin: 0;
  padding-left: 20px;
}

.design-notes li {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #666;
}

.design-notes strong {
  color: #303133;
}

@media (max-width: 768px) {
  .modern-form .form-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .create-btn,
  .advanced-btn {
    width: 100%;
    text-align: center;
  }
  
  .shortcuts-hint {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .recent-list {
    justify-content: center;
  }
}
</style> 