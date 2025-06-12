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
import re
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
    
    def cancel(self):
        """取消任务"""
        self.cancelled = True
        self.status = "cancelled"
    
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
            
            # 创建OpenAI客户端
            client = AsyncOpenAI(
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
                    # 调用大模型API
                    generated_text = await self._generate_single_text(client, task.request)
                    task.generated_texts.append(generated_text)
                    task.current_count += 1
                    task.progress = int((task.current_count / task.total_count) * 100)
                    
                    # 发送进度更新
                    status_data = task.get_status().model_dump()
                    status_data['latest_text'] = generated_text.model_dump()
                    yield f"data: {json.dumps(status_data)}\n\n"
                    
                except Exception as e:
                    logger.error(f"生成第 {i+1} 条数据时出错: {str(e)}")
                    # 继续生成其他数据，不因单条失败而中断
                    continue
            
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
            # 延迟清理任务（给前端时间获取最终状态）
            asyncio.create_task(self._delayed_cleanup(task_id, 60))
    
    async def _generate_single_text(self, client: AsyncOpenAI, request: GenerateRequest) -> GeneratedText:
        """生成单条文本数据"""
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
            
            # 解析文本和标签
            parsed_text, parsed_labels = self._parse_generated_content(raw_output, request.parse_regex)
            
            return GeneratedText(
                text=parsed_text,
                labels=parsed_labels,
                raw_output=raw_output
            )
            
        except Exception as e:
            logger.error(f"调用大模型API失败: {str(e)}")
            raise
    
    def _parse_generated_content(self, content: str, regex_pattern: Optional[str]) -> tuple[str, Optional[str]]:
        """解析生成的内容，提取文本和标签"""
        if not regex_pattern:
            # 没有正则表达式，使用默认解析逻辑
            return self._default_parse(content)
        
        try:
            # 使用自定义正则表达式解析
            pattern = re.compile(regex_pattern, re.DOTALL | re.MULTILINE)
            match = pattern.search(content)
            
            if match:
                groups = match.groups()
                if len(groups) >= 1:
                    text = groups[0].strip()
                    labels = groups[1].strip() if len(groups) >= 2 else None
                    return text, labels
            
            # 正则匹配失败，使用默认解析
            return self._default_parse(content)
            
        except re.error as e:
            logger.warning(f"正则表达式解析失败: {str(e)}, 使用默认解析")
            return self._default_parse(content)
    
    def _default_parse(self, content: str) -> tuple[str, Optional[str]]:
        """默认解析逻辑"""
        # 简单的默认解析：假设内容就是文本，没有特殊格式
        text = content.strip()
        
        # 尝试提取可能的标签格式，如：[标签1,标签2] 或 标签：xxx
        label_patterns = [
            r'\[([^\]]+)\]',  # [标签1,标签2]
            r'标签[：:]\s*([^\n]+)',  # 标签：xxx
            r'分类[：:]\s*([^\n]+)',  # 分类：xxx
            r'类别[：:]\s*([^\n]+)',  # 类别：xxx
        ]
        
        for pattern in label_patterns:
            match = re.search(pattern, text)
            if match:
                labels = match.group(1).strip()
                # 从文本中移除标签部分
                text = re.sub(pattern, '', text).strip()
                return text, labels
        
        return text, None
    
    async def _delayed_cleanup(self, task_id: str, delay_seconds: int):
        """延迟清理任务"""
        await asyncio.sleep(delay_seconds)
        self.cleanup_task(task_id)


# 全局生成服务实例
generation_service = GenerationService() 