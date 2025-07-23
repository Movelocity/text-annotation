# 验证批次存储方式修改

## 修改内容
将 `VerificationService` 中的验证批次和任务存储从数据库改为全局变量存储。

## 修改原因
- 简化存储逻辑，避免数据库操作
- 提高性能，减少数据库查询
- 临时存储，不需要持久化

## 修改详情

### 全局变量
```python
_verification_tasks: Dict[int, List[Dict]] = {}  # 存储任务列表
_verification_batches: Dict[int, Dict] = {}      # 存储批次信息
_next_batch_id = 1                               # 批次ID计数器
```

### 修改的方法
1. `create_verification_batch()` - 创建批次和任务到全局变量
2. `get_batch_progress()` - 从全局变量获取进度
3. `process_verification_tasks()` - 从全局变量获取和处理任务
4. `get_all_batches()` - 从全局变量获取所有批次

### 数据结构
- 批次信息：包含 id, target_label, total_tasks, completed_tasks, status, created_at, updated_at
- 任务信息：包含 id, batch_id, annotation_id, text, original_label, processed, is_correct, processed_at

## 注意事项
- 全局变量在服务重启后会丢失
- 适合临时验证任务，不需要持久化存储
- 移除了对 VerificationBatch 和 VerificationTask 模型的依赖

## 批量处理优化

### 新增功能
1. `check_batch_label(texts: List[str], label: str) -> List[bool]` - 批量验证函数
2. `process_verification_tasks(batch_id: int, batch_size: int = 10) -> int` - 支持批量处理

### 优化内容
- 将单个任务处理改为批量处理，提高效率
- 支持自定义批量大小，默认10个任务一批
- 批量调用验证API，减少网络开销
- 失败时捕获异常并跳过，保证整体流程不中断
- 按顺序处理批量响应结果

### 处理流程
1. 将未处理任务按batch_size分组
2. 每组提取文本列表，调用check_batch_label
3. 按顺序处理返回的布尔值结果
4. 单个任务失败不影响其他任务
5. 批量处理失败不影响下一批处理 