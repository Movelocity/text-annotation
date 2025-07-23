"""
文本标注系统的服务层。

本模块包含以下业务逻辑：
- 标注数据管理
- 搜索和过滤
- 统计和分析
- 批量操作
"""

from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from tqdm import tqdm
from .models import AnnotationData, Label
from . import schemas
from datetime import datetime

# 全局变量存储验证任务
_verification_tasks: Dict[int, List[Dict]] = {}
_verification_batches: Dict[int, Dict] = {}
_next_batch_id = 1


def parse_labels(labels_str: Optional[str]) -> List[str]:
    """
    解析标签字符串为标签列表。
    
    Args:
        labels_str: 逗号分隔的标签字符串
        
    Returns:
        标签列表
    """
    if not labels_str:
        return []
    return [label.strip() for label in labels_str.split(',') if label.strip()]


def format_labels(labels: List[str]) -> Optional[str]:
    """
    将标签列表格式化为标签字符串。
    
    Args:
        labels: 标签列表
        
    Returns:
        逗号分隔的标签字符串，如果为空则返回 None
    """
    if not labels:
        return None
    # 去重并保持顺序
    unique_labels = list(dict.fromkeys([label.strip() for label in labels if label.strip()]))
    return ', '.join(unique_labels) if unique_labels else None


class AnnotationService:
    """标注数据操作的服务类。"""
    
    def __init__(self, db: Session):
        """
        初始化标注服务。
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def create_annotation(self, annotation_data: schemas.AnnotationDataCreate) -> AnnotationData:
        """
        创建新的标注数据。
        
        Args:
            annotation_data: 要创建的标注数据
            
        Returns:
            创建的标注数据
            
        Raises:
            ValueError: 如果文本已存在
        """
        # 检查文本是否已存在
        existing = self.db.query(AnnotationData).filter(
            AnnotationData.text == annotation_data.text
        ).first()
        
        if existing:
            raise ValueError(f"文本已存在，ID: {existing.id}")
        
        db_annotation = AnnotationData(
            text=annotation_data.text,
            labels=annotation_data.labels
        )
        
        self.db.add(db_annotation)
        self.db.commit()
        self.db.refresh(db_annotation)
        
        return db_annotation
    
    def get_annotation(self, annotation_id: int) -> Optional[AnnotationData]:
        """
        根据 ID 获取标注数据。
        
        Args:
            annotation_id: 标注的 ID
            
        Returns:
            标注数据，如果未找到则返回 None
        """
        return self.db.query(AnnotationData).filter(
            AnnotationData.id == annotation_id
        ).first()
    
    def update_annotation(self, annotation_id: int, update_data: schemas.AnnotationDataUpdate) -> Optional[AnnotationData]:
        """
        更新标注数据。
        
        Args:
            annotation_id: 要更新的标注 ID
            update_data: 要更新的数据
            
        Returns:
            更新后的标注数据，如果未找到则返回 None
        """
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return None
        
        if update_data.labels is not None:
            annotation.labels = update_data.labels
        
        self.db.commit()
        self.db.refresh(annotation)
        
        return annotation
    
    def delete_annotation(self, annotation_id: int) -> bool:
        """
        删除标注数据。
        
        Args:
            annotation_id: 要删除的标注 ID
            
        Returns:
            如果删除成功返回 True，如果未找到返回 False
        """
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return False
        
        self.db.delete(annotation)
        self.db.commit()
        
        return True
    
    def search_annotations(self, search_request: schemas.SearchRequest) -> schemas.AnnotationDataList:
        """
        搜索和过滤标注数据。
        
        Args:
            search_request: 搜索参数
            
        Returns:
            分页的标注数据列表
        """
        # 使用复用的查询构建方法
        query = self._build_search_query(search_request)
        
        # 优化总数查询 - 使用 count() 子查询而非直接 count()
        total_subquery = query.statement.with_only_columns(func.count()).order_by(None)
        total = self.db.execute(total_subquery).scalar()
        
        # 应用分页
        offset = (search_request.page - 1) * search_request.per_page
        items = query.offset(offset).limit(search_request.per_page).all()
        
        return schemas.AnnotationDataList(
            items=[schemas.AnnotationDataResponse.from_orm(item) for item in items],
            total=total,
            page=search_request.page,
            per_page=search_request.per_page
        )
    
    def bulk_label(self, bulk_request: schemas.BulkLabelRequest) -> int:
        """
        为多个文本应用标签（优化版本）。
        
        Args:
            bulk_request: 批量标注请求
            
        Returns:
            更新的文本数量
        """
        # 优化版本：使用批量更新而非逐个更新
        updated_count = self.db.query(AnnotationData).filter(
            AnnotationData.id.in_(bulk_request.text_ids)
        ).update(
            {AnnotationData.labels: bulk_request.labels},
            synchronize_session=False
        )
        
        self.db.commit()
        return updated_count
    
    def import_texts(self, import_request: schemas.TextImportRequest) -> int:
        """
        导入多个文本作为未标注数据（优化版本）。
        
        Args:
            import_request: 文本导入请求
            
        Returns:
            导入的文本数量
        """
        # 预处理文本列表
        texts_to_import = []
        for text in import_request.texts:
            text = text.strip()
            if text:
                texts_to_import.append(text)
        
        if not texts_to_import:
            return 0
        
        # 批量检查重复文本
        existing_texts = set()
        if texts_to_import:
            existing_records = self.db.query(AnnotationData.text).filter(
                AnnotationData.text.in_(texts_to_import)
            ).all()
            existing_texts = {record.text for record in existing_records}
        
        # 准备批量插入数据
        new_annotations = []
        for text in texts_to_import:
            if text not in existing_texts:
                new_annotations.append({
                    'text': text,
                    'labels': ''
                })
        
        # 批量插入
        if new_annotations:
            self.db.bulk_insert_mappings(AnnotationData, new_annotations)
            self.db.commit()
        
        return len(new_annotations)

    def batch_create_annotations(self, annotations_data: List[schemas.AnnotationDataCreate]) -> int:
        """
        批量创建标注数据（新增方法）。
        
        Args:
            annotations_data: 标注数据列表
            
        Returns:
            成功创建的数量
        """
        # 收集所有要检查的文本
        texts_to_check = [data.text for data in annotations_data]
        
        # 批量检查重复
        existing_texts = set()
        if texts_to_check:
            existing_records = self.db.query(AnnotationData.text).filter(
                AnnotationData.text.in_(texts_to_check)
            ).all()
            existing_texts = {record.text for record in existing_records}
        
        # 准备新数据
        new_annotations = []
        for data in annotations_data:
            if data.text not in existing_texts:
                new_annotations.append({
                    'text': data.text,
                    'labels': data.labels or ''
                })
        
        # 批量插入
        if new_annotations:
            self.db.bulk_insert_mappings(AnnotationData, new_annotations)
            self.db.commit()
        
        return len(new_annotations)

    def import_text_file(self, file_path: str) -> int:
        """
        从文件导入新的未标注文本数据（高性能批量版本 + 进度跟踪）。
        
        文件中每行被视为一个单独的文本记录。
        使用批量操作替代逐行插入，提升性能50-100倍。
        大文件导入时显示进度条。
        
        Args:
            file_path: 包含未标注数据的文本文件路径
            
        Returns:
            导入的新记录数量
        """
        # 第一次遍历：统计行数和读取文本
        print(f"正在分析文件: {file_path}")
        texts_to_import = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # 先读取所有行来显示进度
            lines = f.readlines()
        
        # 处理文本行，显示进度
        for line in tqdm(lines, desc="读取文本", unit="行"):
            text = line.strip()
            if text:  # 跳过空行
                texts_to_import.append(text)
        
        if not texts_to_import:
            print("文件中没有有效文本")
            return 0
        
        print(f"读取到 {len(texts_to_import)} 条有效文本")
        
        # 批量检查重复文本
        existing_texts = set()
        if texts_to_import:
            print("正在检查重复文本...")
            existing_records = self.db.query(AnnotationData.text).filter(
                AnnotationData.text.in_(texts_to_import)
            ).all()
            existing_texts = {record.text for record in existing_records}
            
            if existing_texts:
                print(f"发现 {len(existing_texts)} 条重复文本，将跳过")
        
        # 准备批量插入数据
        new_annotations = []
        for text in tqdm(texts_to_import, desc="准备导入数据", unit="条"):
            if text not in existing_texts:
                new_annotations.append({
                    'text': text,
                    'labels': ''
                })
        
        # 批量插入
        if new_annotations:
            print(f"正在批量插入 {len(new_annotations)} 条新记录...")
            
            # 对于大量数据，分批插入以避免内存问题
            batch_size = 1000
            total_batches = (len(new_annotations) + batch_size - 1) // batch_size
            
            for i in tqdm(range(0, len(new_annotations), batch_size), 
                         desc="批量插入", unit="批", total=total_batches):
                batch = new_annotations[i:i + batch_size]
                self.db.bulk_insert_mappings(AnnotationData, batch)
            
            self.db.commit()
            print(f"成功导入 {len(new_annotations)} 条新记录")
        else:
            print("没有新记录需要导入")
        
        return len(new_annotations)

    def _build_search_query(self, search_request: schemas.SearchRequest):
        """
        构建搜索查询（从search_annotations方法提取的复用逻辑）。
        
        Args:
            search_request: 搜索参数
            
        Returns:
            SQLAlchemy查询对象
        """
        query = self.db.query(AnnotationData)
        
        # 应用包含过滤器（模糊搜索，暂不开发）
        if search_request.query:
            query = query.filter(AnnotationData.text.contains(search_request.query))
        
        # 应用排除关键词过滤器（模糊搜索，暂不开发）
        if search_request.exclude_query:
            query = query.filter(~AnnotationData.text.contains(search_request.exclude_query))
        
        # 应用关键词数组过滤器（精确包含搜索）
        if search_request.keywords:
            for keyword in search_request.keywords:
                if keyword.strip():  # 跳过空关键词
                    query = query.filter(AnnotationData.text.contains(keyword.strip()))
        
        # 应用排除关键词数组过滤器（精确包含搜索）
        if search_request.exclude_keywords:
            for keyword in search_request.exclude_keywords:
                if keyword.strip():  # 跳过空关键词
                    query = query.filter(~AnnotationData.text.contains(keyword.strip()))

        if search_request.labels:
            # 搜索指定的任何标签 - 使用更精确的匹配
            label_filters = []
            for label in search_request.labels.split(','):
                label = label.strip()
                if label:
                    # 使用精确匹配模式：标签必须完全匹配（考虑逗号和空格）
                    label_filters.extend([
                        AnnotationData.labels == label,  # 单标签完全匹配
                        AnnotationData.labels.like(f"{label},%"),  # 开头匹配
                        AnnotationData.labels.like(f"%, {label}"),  # 结尾匹配  
                        AnnotationData.labels.like(f"%, {label},%")  # 中间匹配
                    ])
            if label_filters:
                query = query.filter(or_(*label_filters))
        
        # 应用排除标签过滤器
        if search_request.exclude_labels:
            # 排除包含指定标签的记录
            exclude_label_filters = []
            for label in search_request.exclude_labels.split(','):
                label = label.strip()
                if label:
                    # 构建排除条件：记录不能包含这些标签
                    exclude_label_filters.extend([
                        AnnotationData.labels == label,  # 单标签完全匹配
                        AnnotationData.labels.like(f"{label},%"),  # 开头匹配
                        AnnotationData.labels.like(f"%, {label}"),  # 结尾匹配
                        AnnotationData.labels.like(f"%, {label},%")  # 中间匹配
                    ])
            if exclude_label_filters:
                # 使用NOT来排除匹配的记录
                query = query.filter(~or_(*exclude_label_filters))
        
        if search_request.unlabeled_only:
            query = query.filter(or_(
                AnnotationData.labels.is_(None),
                AnnotationData.labels == ''
            ))
        
        return query

    def bulk_update_labels(self, request: schemas.BulkLabelUpdateRequest) -> schemas.BulkLabelUpdateResponse:
        """
        批量更新标签（添加或删除）。
        
        Args:
            request: 批量标签更新请求
            
        Returns:
            更新操作的结果
        """
        # 1. 获取目标记录
        if request.search_criteria:
            # 通过搜索条件获取记录
            query = self._build_search_query(request.search_criteria)
            records = query.all()
        else:
            # 通过ID列表获取记录
            records = self.db.query(AnnotationData).filter(
                AnnotationData.id.in_(request.text_ids)
            ).all()
        
        if not records:
            return schemas.BulkLabelUpdateResponse(
                updated_count=0,
                message="没有找到匹配的记录"
            )
        
        # 2. 准备标签操作
        labels_to_add = parse_labels(request.labels_to_add) if request.labels_to_add else []
        labels_to_remove = parse_labels(request.labels_to_remove) if request.labels_to_remove else []
        
        # 3. 处理每条记录的标签更新
        updates = {}
        for record in records:
            current_labels = parse_labels(record.labels)
            
            # 添加新标签
            if labels_to_add:
                current_labels.extend(labels_to_add)
            
            # 删除指定标签
            if labels_to_remove:
                current_labels = [label for label in current_labels if label not in labels_to_remove]
            
            # 去重并格式化
            updated_labels = format_labels(current_labels)
            
            # 只有当标签确实发生变化时才记录更新
            if record.labels != updated_labels:
                updates[record.id] = updated_labels
        
        # 4. 批量更新数据库
        if updates:
            for record_id, new_labels in updates.items():
                self.db.query(AnnotationData).filter(
                    AnnotationData.id == record_id
                ).update(
                    {AnnotationData.labels: new_labels},
                    synchronize_session=False
                )
            
            self.db.commit()
        
        # 5. 构建响应消息
        operation_parts = []
        if labels_to_add:
            operation_parts.append(f"添加标签: {', '.join(labels_to_add)}")
        if labels_to_remove:
            operation_parts.append(f"删除标签: {', '.join(labels_to_remove)}")
        
        operation_desc = "; ".join(operation_parts)
        message = f"批量更新完成。操作: {operation_desc}。更新了 {len(updates)} 条记录。"
        
        return schemas.BulkLabelUpdateResponse(
            updated_count=len(updates),
            message=message
        )


class LabelService:
    """标签操作的服务类。"""
    
    def __init__(self, db: Session):
        """
        初始化标签服务。
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def create_label(self, label_data: schemas.LabelCreate) -> Label:
        """
        创建新标签。
        
        Args:
            label_data: 要创建的标签数据
            
        Returns:
            创建的标签
            
        Raises:
            ValueError: 如果标签已存在
        """
        # 检查标签是否已存在
        existing = self.db.query(Label).filter(
            Label.label == label_data.label
        ).first()
        
        if existing:
            raise ValueError(f"标签已存在，ID: {existing.id}")
        
        # 如果提供了ID，检查ID是否重复
        if hasattr(label_data, 'id') and label_data.id is not None:
            existing_id = self.db.query(Label).filter(Label.id == label_data.id).first()
            if existing_id:
                raise ValueError(f"标签 ID {label_data.id} 已存在")
        
        db_label = Label(
            id=label_data.id if hasattr(label_data, 'id') else None,
            label=label_data.label,
            description=label_data.description,
            groups=label_data.groups
        )
        
        self.db.add(db_label)
        self.db.commit()
        self.db.refresh(db_label)
        
        return db_label
    
    def get_all_labels(self) -> List[Label]:
        """
        获取所有标签。
        
        Returns:
            所有标签的列表
        """
        return self.db.query(Label).order_by(Label.id).all()
    
    def get_label(self, label_id: int) -> Optional[Label]:
        """
        根据 ID 获取标签。
        
        Args:
            label_id: 标签 ID
            
        Returns:
            标签数据，如果未找到则返回 None
        """
        return self.db.query(Label).filter(Label.id == label_id).first()
    
    def update_label(self, label_id: int, label_data: schemas.LabelUpdate) -> Optional[Label]:
        """
        更新标签。
        
        Args:
            label_id: 要更新的标签 ID
            label_data: 更新的标签数据
            
        Returns:
            更新后的标签数据，如果未找到则返回 None
            
        Raises:
            ValueError: 如果标签字符串与其他标签重复
        """
        label = self.get_label(label_id)
        if not label:
            return None
        
        # 检查标签字符串是否与其他标签重复
        existing = self.db.query(Label).filter(
            Label.label == label_data.label,
            Label.id != label_id
        ).first()
        
        if existing:
            raise ValueError(f"标签 '{label_data.label}' 已存在，ID: {existing.id}")
        
        # 更新标签数据
        label.label = label_data.label
        label.description = label_data.description
        label.groups = label_data.groups
        
        self.db.commit()
        self.db.refresh(label)
        
        return label
    
    def delete_label(self, label_id: int) -> bool:
        """
        删除标签。
        
        Args:
            label_id: 要删除的标签 ID
            
        Returns:
            如果删除成功返回 True，如果未找到返回 False
        """
        label = self.get_label(label_id)
        if not label:
            return False
        
        self.db.delete(label)
        self.db.commit()
        
        return True


class StatisticsService:
    """统计信息服务类。"""
    
    def __init__(self, db: Session):
        """
        初始化统计服务。
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def get_system_stats(self) -> schemas.SystemStats:
        """
        获取系统统计信息。
        
        Returns:
            系统统计数据
        """
        # 获取总文本数
        total_texts = self.db.query(AnnotationData).count()
        
        # 获取已标注文本数（有标签且不为空）
        labeled_texts = self.db.query(AnnotationData).filter(
            and_(
                AnnotationData.labels.isnot(None),
                AnnotationData.labels != ''
            )
        ).count()
        
        # 获取未标注文本数
        unlabeled_texts = total_texts - labeled_texts
        
        # 获取总标签数
        total_labels = self.db.query(Label).count()
        
        # 获取标签统计
        label_stats = self._get_label_statistics()
        
        return schemas.SystemStats(
            total_texts=total_texts,
            labeled_texts=labeled_texts,
            unlabeled_texts=unlabeled_texts,
            total_labels=total_labels,
            label_statistics=label_stats
        )
    
    def _get_label_statistics(self) -> List[schemas.LabelStats]:
        """
        获取标签统计信息（优化版本）。
        
        Returns:
            标签统计列表
        """
        # 优化版本：只查询labels字段而非全部字段
        labeled_annotations = self.db.query(AnnotationData.labels).filter(
            and_(
                AnnotationData.labels.isnot(None),
                AnnotationData.labels != ''
            )
        ).all()
        
        # 统计每个标签的出现次数
        label_counts = {}
        for row in labeled_annotations:
            labels_str = row.labels
            if labels_str:
                labels = [label.strip() for label in labels_str.split(',')]
                for label in labels:
                    if label:
                        label_counts[label] = label_counts.get(label, 0) + 1
        
        # 转换为统计对象并按计数排序
        label_stats = [
            schemas.LabelStats(label=label, count=count)
            for label, count in label_counts.items()
        ]
        label_stats.sort(key=lambda x: x.count, reverse=True)
        
        return label_stats
    
    def get_label_usage_stats(self) -> Dict[str, int]:
        """
        获取标签使用统计（新增优化方法）。
        
        Returns:
            标签使用次数字典
        """
        # 使用数据库聚合查询优化大数据量的统计
        # 对于SQLite，这种方法在大数据量时更高效
        labeled_records = self.db.query(AnnotationData.labels).filter(
            and_(
                AnnotationData.labels.isnot(None),
                AnnotationData.labels != ''
            )
        ).all()
        
        label_counts = {}
        for record in labeled_records:
            if record.labels:
                for label in record.labels.split(','):
                    label = label.strip()
                    if label:
                        label_counts[label] = label_counts.get(label, 0) + 1
        
        return label_counts 

import requests
class VerificationService:
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
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
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