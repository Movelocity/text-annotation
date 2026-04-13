from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from tqdm import tqdm
from .models import AnnotationData
from . import schemas
from .services import AnnotationService
from datetime import datetime
import requests

# 全局变量存储验证任务
_verification_tasks: Dict[int, List[Dict]] = {}
_verification_batches: Dict[int, Dict] = {}
_next_batch_id = 1


class DiscriminationService:
    """标签验证服务类。"""
    
    def __init__(self, db: Session):
        """
        初始化验证服务。
        
        Args:
            db: 数据库会话
        """
        self.db = db

    def llm_API(self, query: str) -> str:
        """
        调用LLM API进行文本分析。
        
        Args:
            query: 查询文本
            
        Returns:
            API响应文本，失败时返回None
        """
        api_key = "app-mTzrTj2Dy1cXO6O9Y0VGh1I6"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        api_url = "https://gaia.yafex.cn/v1/completion-messages"
        data = {
            "inputs": {
                "query": query
            },
            "response_mode": "blocking",
            "user": "AMAZON_TRANSLATE"
        }
        try:
            response = requests.post(api_url, headers=headers, json=data)
            response.raise_for_status()  # 检查HTTP错误
            result = response.json()
            return result.get("answer", "")
        except requests.exceptions.RequestException as e:
            print(f"API请求错误: {e}")
            return None
        except Exception as e:
            print(f"API调用错误: {e}")
            return None
    
    def create_verification_batch(self, target_label: str, search_criteria: Optional[schemas.SearchRequest] = None) -> schemas.VerifyLabelResponse:
        """
        创建标签验证任务批次。
        
        Args:
            target_label: 要验证的目标标签
            search_criteria: 搜索条件，用于筛选要验证的记录
            
        Returns:
            验证任务批次信息
        """
        global _next_batch_id, _verification_batches, _verification_tasks
        
        # 1. 查找包含目标标签的记录
        query = self.db.query(AnnotationData)
        
        if search_criteria:
            # 使用现有的搜索查询构建方法
            annotation_service = AnnotationService(self.db)
            query = annotation_service._build_search_query(search_criteria)
        
        # 添加标签过滤条件
        label_filters = [
            AnnotationData.labels == target_label,  # 单标签完全匹配
            AnnotationData.labels.like(f"{target_label},%"),  # 开头匹配
            AnnotationData.labels.like(f"%, {target_label}"),  # 结尾匹配  
            AnnotationData.labels.like(f"%, {target_label},%")  # 中间匹配
        ]
        query = query.filter(or_(*label_filters))
        
        # 获取匹配的记录
        matching_records = query.all()
        
        if not matching_records:
            raise ValueError(f"没有找到包含标签 '{target_label}' 的记录")
        
        # 2. 创建验证批次（使用全局变量）
        batch_id = _next_batch_id
        _next_batch_id += 1
        
        batch_info = {
            'id': batch_id,
            'target_label': target_label,
            'total_tasks': len(matching_records),
            'completed_tasks': 0,
            'status': 'pending',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        _verification_batches[batch_id] = batch_info
        
        # 3. 创建验证任务（使用全局变量）
        tasks = []
        for record in matching_records:
            task = {
                'id': len(tasks) + 1,
                'batch_id': batch_id,
                'annotation_id': record.id,
                'text': record.text,
                'original_label': record.labels,
                'processed': False,
                'is_correct': None,
                'processed_at': None
            }
            tasks.append(task)
        
        _verification_tasks[batch_id] = tasks
        
        return schemas.VerifyLabelResponse(
            batch_id=batch_id,
            target_label=target_label,
            total_tasks=len(matching_records),
            message=f"成功创建验证批次，包含 {len(matching_records)} 个任务"
        )
    
    def get_batch_progress(self, batch_id: int) -> Optional[schemas.BatchProgressResponse]:
        """
        获取批次进度。
        
        Args:
            batch_id: 批次ID
            
        Returns:
            批次进度信息，如果未找到则返回 None
        """
        global _verification_batches
        
        batch = _verification_batches.get(batch_id)
        
        if not batch:
            return None
        
        # 计算进度百分比
        progress_percentage = 0.0
        if batch['total_tasks'] > 0:
            progress_percentage = (batch['completed_tasks'] / batch['total_tasks']) * 100
        
        return schemas.BatchProgressResponse(
            batch_id=batch['id'],
            target_label=batch['target_label'],
            total_tasks=batch['total_tasks'],
            completed_tasks=batch['completed_tasks'],
            status=batch['status'],
            progress_percentage=round(progress_percentage, 2),
            created_at=batch['created_at'].isoformat(),
            updated_at=batch['updated_at'].isoformat()
        )
    
    
    def check_batch_label(self, texts: List[str], label: str) -> List[bool]:
        """
        批量检查文本和标签的匹配关系。
        
        Args:
            texts: 要检查的文本列表
            label: 要验证的标签
            
        Returns:
            布尔值列表，True表示标签正确，False表示标签错误
        """
        if not texts:
            return []
        
        print(f"    开始批量验证 {len(texts)} 个文本，目标标签: {label}")
        
        # 构造批量查询文本
        batch_text = ""
        for i, text in enumerate(texts, 1):
            batch_text += f"<Text_{i}>{text}</Text_{i}>"
        
        # 构造查询提示
        query = f"""{batch_text}"""
        
        try:
            # 调用LLM API
            print(f"    调用LLM API...")
            response = self.llm_API(query)
            
            if not response:
                print(f"    LLM API调用失败，返回默认结果")
                # 如果API调用失败，返回默认结果（假设标签正确）
                return [True] * len(texts)
            
            print(f"    LLM API响应长度: {len(response)}")
            
            # 解析响应中的标签
            predicted_labels = self._parse_batch_labels(response, len(texts))
            print(f"    解析出的标签: {predicted_labels}")
            
            # 比较预测标签与目标标签
            results = []
            for i, predicted_label in enumerate(predicted_labels):
                # 检查预测标签是否与目标标签匹配
                is_correct = predicted_label.lower().strip() == label.lower().strip()
                results.append(is_correct)
                print(f"      文本{i+1}: 预测='{predicted_label}', 目标='{label}', 正确={is_correct}")
            
            return results
            
        except Exception as e:
            print(f"    批量标签验证出错: {e}")
            # 出错时返回默认结果（假设标签正确）
            return [True] * len(texts)
    
    def _parse_batch_labels(self, response: str, expected_count: int) -> List[str]:
        """
        解析批量标签响应。
        
        Args:
            response: LLM API的响应文本
            expected_count: 期望的标签数量
            
        Returns:
            解析出的标签列表
        """
        import re
        
        # 使用正则表达式提取标签
        pattern = r'<Label_(\d+)>(.*?)</Label_\1>'
        matches = re.findall(pattern, response)
        
        # 按标签编号排序
        matches.sort(key=lambda x: int(x[0]))
        
        # 提取标签内容
        labels = [match[1].strip() for match in matches]
        
        # 如果解析的标签数量与期望不符，返回空标签列表
        if len(labels) != expected_count:
            print(f"警告：期望 {expected_count} 个标签，但解析到 {len(labels)} 个")
            # 补充缺失的标签
            while len(labels) < expected_count:
                labels.append("")
        
        return labels[:expected_count]  # 确保返回正确数量的标签
    
    def process_verification_tasks(self, batch_id: int, batch_size: int = 10) -> int:
        """
        处理验证任务批次。
        
        Args:
            batch_id: 批次ID
            batch_size: 批量处理的大小，默认10
            
        Returns:
            处理的任务数量
        """
        global _verification_batches, _verification_tasks
        
        # 1. 获取批次信息
        batch = _verification_batches.get(batch_id)
        
        if not batch:
            raise ValueError(f"批次 {batch_id} 不存在")
        
        if batch['status'] == 'completed':
            return 0
        
        # 2. 更新批次状态为运行中
        batch['status'] = 'running'
        batch['updated_at'] = datetime.now()
        
        # 3. 获取未处理的任务
        tasks = _verification_tasks.get(batch_id, [])
        unprocessed_tasks = [task for task in tasks if not task['processed']]
        
        if not unprocessed_tasks:
            batch['status'] = 'completed'
            return 0
        
        # 4. 批量处理任务
        processed_count = 0
        total_unprocessed = len(unprocessed_tasks)
        
        print(f"开始处理批次 {batch_id}，共 {total_unprocessed} 个未处理任务，批次大小: {batch_size}")
        
        for i in range(0, total_unprocessed, batch_size):
            batch_tasks = unprocessed_tasks[i:i + batch_size]
            current_batch_num = i // batch_size + 1
            total_batches = (total_unprocessed + batch_size - 1) // batch_size
            
            print(f"处理第 {current_batch_num}/{total_batches} 批，包含 {len(batch_tasks)} 个任务")
            
            try:
                # 提取文本列表
                texts = [task['text'] for task in batch_tasks]
                
                # 批量调用验证函数
                print(f"  调用LLM API验证 {len(texts)} 个文本...")
                results = self.check_batch_label(texts, batch['target_label'])
                print(f"  获得验证结果: {results}")
                
                # 按顺序处理结果
                for j, (task, is_correct) in enumerate(zip(batch_tasks, results)):
                    try:
                        # 更新任务结果
                        task['is_correct'] = is_correct
                        task['processed'] = True
                        task['processed_at'] = datetime.now()
                        
                        # 如果标签错误，更新标注数据
                        if not is_correct:
                            annotation = self.db.query(AnnotationData).filter(
                                AnnotationData.id == task['annotation_id']
                            ).first()
                            
                            if annotation:
                                # 将标签改为"other"
                                annotation.labels = "other"
                                print(f"      更新标注ID {task['annotation_id']} 的标签为 'other'")
                        
                        processed_count += 1
                        
                    except Exception as e:
                        # 记录错误但继续处理其他任务
                        print(f"处理任务 {task['id']} 时出错: {e}")
                        continue
                
                # 提交数据库更改
                self.db.commit()
                print(f"  第 {current_batch_num} 批处理完成，成功处理 {processed_count} 个任务，数据库已提交")
                
            except Exception as e:
                # 记录批量处理错误但继续处理下一批
                print(f"批量处理任务时出错: {e}")
                # 回滚事务
                self.db.rollback()
                continue
        
        # 5. 更新批次进度
        batch['completed_tasks'] += processed_count
        
        # 检查是否所有任务都已完成
        if batch['completed_tasks'] >= batch['total_tasks']:
            batch['status'] = 'completed'
        
        batch['updated_at'] = datetime.now()
        
        return processed_count
    
    def check_text_label(self, text: str, label: str) -> bool:
        """
        检查单个文本和标签的匹配关系。
        
        Args:
            text: 要检查的文本
            label: 要验证的标签
            
        Returns:
            True表示标签正确，False表示标签错误
        """
        # 构造查询文本
        query = f"<Text>{text}</Text>"
        
        try:
            # 调用LLM API
            response = self.llm_API(query)
            
            if not response:
                # 如果API调用失败，返回默认结果（假设标签正确）
                return True
            
            # 解析响应中的标签
            predicted_label = self._parse_single_label(response)
            
            # 检查预测标签是否与目标标签匹配
            is_correct = predicted_label.lower().strip() == label.lower().strip()
            
            return is_correct
            
        except Exception as e:
            print(f"单个文本标签验证出错: {e}")
            # 出错时返回默认结果（假设标签正确）
            return True
    
    def _parse_single_label(self, response: str) -> str:
        """
        解析单个标签响应。
        
        Args:
            response: LLM API的响应文本
            
        Returns:
            解析出的标签
        """
        import re
        
        # 使用正则表达式提取标签
        pattern = r'<Label>(.*?)</Label>'
        match = re.search(pattern, response)
        
        if match:
            return match.group(1).strip()
        else:
            # 如果没有找到标签标签，尝试直接提取文本
            return response.strip()
    
    def get_all_batches(self) -> List[schemas.BatchProgressResponse]:
        """
        获取所有验证批次。
        
        Returns:
            所有批次的进度信息
        """
        global _verification_batches
        
        result = []
        for batch_id, batch in sorted(_verification_batches.items(), key=lambda x: x[1]['created_at'], reverse=True):
            progress_percentage = 0.0
            if batch['total_tasks'] > 0:
                progress_percentage = (batch['completed_tasks'] / batch['total_tasks']) * 100
            
            result.append(schemas.BatchProgressResponse(
                batch_id=batch['id'],
                target_label=batch['target_label'],
                total_tasks=batch['total_tasks'],
                completed_tasks=batch['completed_tasks'],
                status=batch['status'],
                progress_percentage=round(progress_percentage, 2),
                created_at=batch['created_at'].isoformat(),
                updated_at=batch['updated_at'].isoformat()
            ))
        
        return result 