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
from .models import AnnotationData, Label
from . import schemas


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
        query = self.db.query(AnnotationData)
        
        # 应用过滤器
        if search_request.query:
            query = query.filter(AnnotationData.text.contains(search_request.query))
        
        if search_request.labels:
            # 搜索指定的任何标签
            label_filters = []
            for label in search_request.labels.split(','):
                label = label.strip()
                label_filters.append(AnnotationData.labels.contains(label))
            query = query.filter(or_(*label_filters))
        
        if search_request.unlabeled_only:
            query = query.filter(or_(
                AnnotationData.labels.is_(None),
                AnnotationData.labels == ''
            ))
        
        # 获取总数
        total = query.count()
        
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
        为多个文本应用标签。
        
        Args:
            bulk_request: 批量标注请求
            
        Returns:
            更新的文本数量
        """
        updated_count = 0
        
        for text_id in bulk_request.text_ids:
            annotation = self.get_annotation(text_id)
            if annotation:
                annotation.labels = bulk_request.labels
                updated_count += 1
        
        self.db.commit()
        return updated_count
    
    def import_texts(self, import_request: schemas.TextImportRequest) -> int:
        """
        导入多个文本作为未标注数据。
        
        Args:
            import_request: 文本导入请求
            
        Returns:
            导入的文本数量
        """
        imported_count = 0
        
        for text in import_request.texts:
            text = text.strip()
            if text:
                # 检查文本是否已存在
                existing = self.db.query(AnnotationData).filter(
                    AnnotationData.text == text
                ).first()
                
                if not existing:
                    db_annotation = AnnotationData(text=text, labels='')
                    self.db.add(db_annotation)
                    imported_count += 1
        
        self.db.commit()
        return imported_count


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
            label=label_data.label
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
        获取标签统计信息。
        
        Returns:
            标签统计列表
        """
        # 获取所有已标注的文本
        labeled_annotations = self.db.query(AnnotationData).filter(
            and_(
                AnnotationData.labels.isnot(None),
                AnnotationData.labels != ''
            )
        ).all()
        
        # 统计每个标签的出现次数
        label_counts = {}
        for annotation in labeled_annotations:
            if annotation.labels:
                labels = [label.strip() for label in annotation.labels.split(',')]
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