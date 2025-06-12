"""
数据生成服务模块

本模块提供以下功能：
- 大模型API调用
- 流式数据生成
- 文本解析和标签提取
- 生成任务管理和取消
"""

import asyncio
import json
import uuid
from typing import AsyncGenerator, Dict, List, Optional, Any
from datetime import datetime
import logging

from openai import AsyncOpenAI
import httpx
from pydantic import ValidationError

from .schemas import GenerateRequest, GeneratedText, GenerateStatus

logger = logging.getLogger(__name__)


class GenerationTask:
    """生成任务类，用于管理单个生成任务的状态"""
    
    def __init__(self, task_id: str, request: GenerateRequest):
        self.task_id = task_id
        self.request = request
        self.status = "pending"
        self.progress = 0
        self.current_count = 0
        self.total_count = request.count
        self.generated_texts: List[GeneratedText] = []
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.cancelled = False
        self.client: Optional[AsyncOpenAI] = None
        self.current_generation_task: Optional[asyncio.Task] = None
    
    def cancel(self):
        """取消任务和清理资源"""
        self.cancelled = True
        self.status = "cancelled"
        
        # 取消当前的生成任务
        if self.current_generation_task and not self.current_generation_task.done():
            self.current_generation_task.cancel()
        
        # 关闭OpenAI客户端连接
        if self.client:
            asyncio.create_task(self._cleanup_client())
    
    async def _cleanup_client(self):
        """清理OpenAI客户端资源"""
        try:
            if self.client:
                await self.client.close()
                self.client = None
                logger.info(f"任务 {self.task_id} 的OpenAI客户端已关闭")
        except Exception as e:
            logger.error(f"清理客户端资源时出错: {str(e)}")
    
    def get_status(self) -> GenerateStatus:
        """获取任务状态"""
        return GenerateStatus(
            status=self.status,
            progress=self.progress,
            current_count=self.current_count,
            total_count=self.total_count,
            message=f"已生成 {self.current_count}/{self.total_count} 条数据",
            error=self.error
        )


class GenerationService:
    """数据生成服务"""
    
    def __init__(self):
        self.active_tasks: Dict[str, GenerationTask] = {}
    
    def create_task(self, request: GenerateRequest) -> str:
        """创建新的生成任务"""
        task_id = str(uuid.uuid4())
        task = GenerationTask(task_id, request)
        self.active_tasks[task_id] = task
        logger.info(f"创建生成任务: {task_id}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[GenerationTask]:
        """获取任务"""
        return self.active_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.get_task(task_id)
        if task:
            task.cancel()
            logger.info(f"取消生成任务: {task_id}")
            return True
        return False
    
    def cleanup_task(self, task_id: str):
        """清理已完成的任务"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
            logger.info(f"清理生成任务: {task_id}")
    
    async def generate_stream(self, task_id: str) -> AsyncGenerator[str, None]:
        """流式生成数据"""
        task = self.get_task(task_id)
        if not task:
            yield f"data: {json.dumps({'error': '任务不存在'})}\n\n"
            return
        
        try:
            task.status = "generating"
            yield f"data: {json.dumps(task.get_status().model_dump())}\n\n"
            
            # 创建OpenAI客户端并保存到任务中
            task.client = AsyncOpenAI(
                api_key=task.request.api_key,
                base_url=task.request.base_url,
                timeout=httpx.Timeout(60.0)
            )
            
            # 批量生成数据
            for i in range(task.request.count):
                if task.cancelled:
                    task.status = "cancelled"
                    yield f"data: {json.dumps(task.get_status().model_dump())}\n\n"
                    break
                
                try:
                    # 创建可取消的生成任务
                    generation_coro = self._generate_single_text(task.client, task.request)
                    task.current_generation_task = asyncio.create_task(generation_coro)
                    
                    # 等待生成完成或被取消
                    generated_text = await task.current_generation_task
                    
                    task.generated_texts.append(generated_text)
                    task.current_count += 1
                    task.progress = int((task.current_count / task.total_count) * 100)
                    
                    # 发送进度更新
                    status_data = task.get_status().model_dump()
                    status_data['latest_text'] = generated_text.model_dump()
                    yield f"data: {json.dumps(status_data)}\n\n"
                    
                except asyncio.CancelledError:
                    logger.info(f"任务 {task_id} 第 {i+1} 条生成被取消")
                    task.status = "cancelled"
                    yield f"data: {json.dumps(task.get_status().model_dump())}\n\n"
                    break
                except Exception as e:
                    logger.error(f"生成第 {i+1} 条数据时出错: {str(e)}")
                    # 继续生成其他数据，不因单条失败而中断
                    continue
                finally:
                    task.current_generation_task = None
            
            # 完成生成
            if not task.cancelled:
                task.status = "completed"
                task.progress = 100
                yield f"data: {json.dumps(task.get_status().model_dump())}\n\n"
            
        except Exception as e:
            logger.error(f"生成任务 {task_id} 出错: {str(e)}")
            task.status = "error"
            task.error = str(e)
            yield f"data: {json.dumps(task.get_status().model_dump())}\n\n"
        
        finally:
            # 清理客户端资源
            if task.client:
                await task._cleanup_client()
            
            # 延迟清理任务（给前端时间获取最终状态）
            asyncio.create_task(self._delayed_cleanup(task_id, 60))
    
    async def _generate_single_text(self, client: AsyncOpenAI, request: GenerateRequest) -> GeneratedText:
        """生成单条文本数据（仅负责API调用，不做解析）"""
        try:
            # 构建请求参数
            messages = [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt}
            ]
            
            kwargs = {
                "model": request.model,
                "messages": messages,
                "temperature": request.temperature,
                "stream": False
            }
            
            if request.max_tokens:
                kwargs["max_tokens"] = request.max_tokens
            
            # 调用API
            response = await client.chat.completions.create(**kwargs)
            
            # 提取生成内容
            raw_output = response.choices[0].message.content or ""
            
            # 只返回原始输出，不进行解析（解析工作交给前端）
            return GeneratedText(
                text=raw_output,  # 原始输出作为text
                labels=None,      # 不在后端解析标签
                raw_output=raw_output
            )
            
        except Exception as e:
            logger.error(f"调用大模型API失败: {str(e)}")
            raise
    
    # 移除解析相关方法，解析工作交给前端处理
    
    async def _delayed_cleanup(self, task_id: str, delay_seconds: int):
        """延迟清理任务"""
        await asyncio.sleep(delay_seconds)
        self.cleanup_task(task_id)


# 全局生成服务实例
generation_service = GenerationService() 