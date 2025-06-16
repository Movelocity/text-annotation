# 预测服务跨域问题解决方案

## 问题描述
前端直接调用 `http://localhost:5000/v1/predict` 推理服务时遇到跨域问题，浏览器拒绝发起请求。

## 解决方案
使用后端代理的方式，让前端调用本地后端API，由后端代为请求推理服务。

### 后端改动

1. **添加依赖**
   - 使用 `uv add httpx` 添加HTTP客户端库

2. **添加schemas** (`server/schemas.py`)
   ```python
   class PredictRequest(BaseModel):
       query: str = Field(..., description="要预测意图的文本")

   class PredictResponse(BaseModel):
       intent: str = Field(..., description="预测的意图")
       prob: float = Field(..., description="预测概率")
       query: str = Field(..., description="原始查询文本")
       result_dict: dict = Field(..., description="所有意图的概率分布")
       status: int = Field(..., description="状态码")

   class PredictConfig(BaseModel):
       base_url: str = Field(..., description="预测服务的基础URL")
       endpoint: str = Field(..., description="预测服务的端点路径")
   ```

3. **添加API端点** (`server/main.py`)
   - `POST /prediction/predict` - 代理预测请求
   - `POST /prediction/test-connection` - 测试预测服务连接

### 前端改动

1. **修改预测服务** (`web/src/services/prediction.ts`)
   - `predict()` 方法改为调用 `/prediction/predict`
   - `testConnection()` 方法改为调用 `/prediction/test-connection`
   - 增加超时时间到30秒

## 优势
1. **解决跨域问题** - 前端只需调用同源的后端API
2. **集中配置管理** - 预测服务配置在后端统一管理
3. **更好的错误处理** - 后端可以提供更友好的错误信息
4. **安全性提升** - 避免在前端暴露外部服务地址

## 使用方式
前端调用方式保持不变：
```typescript
const result = await predictionService.predict("测试文本")
```

后端会自动代理请求到配置的推理服务地址（默认 `http://localhost:5000/v1/predict`）。 