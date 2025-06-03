"""
Service layer for the text annotation system.

This module contains the business logic for:
- Annotation data management
- Search and filtering
- Statistics and analytics
- Bulk operations
"""

from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from models import AnnotationData, Label
import schemas


class AnnotationService:
    """Service class for annotation data operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the annotation service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_annotation(self, annotation_data: schemas.AnnotationDataCreate) -> AnnotationData:
        """
        Create new annotation data.
        
        Args:
            annotation_data: Annotation data to create
            
        Returns:
            Created annotation data
            
        Raises:
            ValueError: If text already exists
        """
        # Check if text already exists
        existing = self.db.query(AnnotationData).filter(
            AnnotationData.text == annotation_data.text
        ).first()
        
        if existing:
            raise ValueError(f"Text already exists with ID: {existing.id}")
        
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
        Get annotation data by ID.
        
        Args:
            annotation_id: ID of the annotation
            
        Returns:
            Annotation data or None if not found
        """
        return self.db.query(AnnotationData).filter(
            AnnotationData.id == annotation_id
        ).first()
    
    def update_annotation(self, annotation_id: int, update_data: schemas.AnnotationDataUpdate) -> Optional[AnnotationData]:
        """
        Update annotation data.
        
        Args:
            annotation_id: ID of the annotation to update
            update_data: Data to update
            
        Returns:
            Updated annotation data or None if not found
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
        Delete annotation data.
        
        Args:
            annotation_id: ID of the annotation to delete
            
        Returns:
            True if deleted, False if not found
        """
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return False
        
        self.db.delete(annotation)
        self.db.commit()
        
        return True
    
    def search_annotations(self, search_request: schemas.SearchRequest) -> schemas.AnnotationDataList:
        """
        Search and filter annotation data.
        
        Args:
            search_request: Search parameters
            
        Returns:
            Paginated list of annotation data
        """
        query = self.db.query(AnnotationData)
        
        # Apply filters
        if search_request.query:
            query = query.filter(AnnotationData.text.contains(search_request.query))
        
        if search_request.labels:
            # Search for any of the specified labels
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
        
        # Get total count
        total = query.count()
        
        # Apply pagination
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
        Apply labels to multiple texts.
        
        Args:
            bulk_request: Bulk labeling request
            
        Returns:
            Number of texts updated
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
        Import multiple texts as unlabeled data.
        
        Args:
            import_request: Text import request
            
        Returns:
            Number of texts imported
        """
        imported_count = 0
        
        for text in import_request.texts:
            text = text.strip()
            if text:
                # Check if text already exists
                existing = self.db.query(AnnotationData).filter(
                    AnnotationData.text == text
                ).first()
                
                if not existing:
                    annotation = AnnotationData(text=text, labels=None)
                    self.db.add(annotation)
                    imported_count += 1
        
        self.db.commit()
        return imported_count


class LabelService:
    """Service class for label management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the label service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_label(self, label_data: schemas.LabelCreate) -> Label:
        """
        Create a new label.
        
        Args:
            label_data: Label data to create
            
        Returns:
            Created label
            
        Raises:
            ValueError: If label already exists
        """
        # Check if label already exists
        existing = self.db.query(Label).filter(
            Label.label == label_data.label
        ).first()
        
        if existing:
            raise ValueError(f"Label already exists with ID: {existing.id}")
        
        # Auto-assign ID if not provided
        if label_data.id is None:
            max_id = self.db.query(func.max(Label.id)).scalar() or 0
            label_id = max_id + 1
        else:
            # Check if ID already exists
            existing_id = self.db.query(Label).filter(
                Label.id == label_data.id
            ).first()
            if existing_id:
                raise ValueError(f"Label ID {label_data.id} already exists")
            label_id = label_data.id
        
        db_label = Label(id=label_id, label=label_data.label)
        self.db.add(db_label)
        self.db.commit()
        self.db.refresh(db_label)
        
        return db_label
    
    def get_all_labels(self) -> List[Label]:
        """
        Get all labels.
        
        Returns:
            List of all labels
        """
        return self.db.query(Label).order_by(Label.id).all()
    
    def get_label(self, label_id: int) -> Optional[Label]:
        """
        Get label by ID.
        
        Args:
            label_id: ID of the label
            
        Returns:
            Label or None if not found
        """
        return self.db.query(Label).filter(Label.id == label_id).first()
    
    def delete_label(self, label_id: int) -> bool:
        """
        Delete a label.
        
        Args:
            label_id: ID of the label to delete
            
        Returns:
            True if deleted, False if not found
        """
        label = self.get_label(label_id)
        if not label:
            return False
        
        self.db.delete(label)
        self.db.commit()
        
        return True


class StatisticsService:
    """Service class for statistics and analytics."""
    
    def __init__(self, db: Session):
        """
        Initialize the statistics service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_system_stats(self) -> schemas.SystemStats:
        """
        Get overall system statistics.
        
        Returns:
            System statistics
        """
        # Get total texts
        total_texts = self.db.query(AnnotationData).count()
        
        # Get labeled vs unlabeled counts
        labeled_texts = self.db.query(AnnotationData).filter(
            and_(
                AnnotationData.labels.isnot(None),
                AnnotationData.labels != ''
            )
        ).count()
        
        unlabeled_texts = total_texts - labeled_texts
        
        # Get total unique labels
        total_labels = self.db.query(Label).count()
        
        # Get label statistics
        label_stats = self._get_label_statistics()
        
        return schemas.SystemStats(
            total_texts=total_texts,
            labeled_texts=labeled_texts,
            unlabeled_texts=unlabeled_texts,
            total_labels=total_labels,
            label_stats=label_stats
        )
    
    def _get_label_statistics(self) -> List[schemas.LabelStats]:
        """
        Get statistics for each label.
        
        Returns:
            List of label statistics
        """
        # Get all annotations with labels
        annotations = self.db.query(AnnotationData).filter(
            and_(
                AnnotationData.labels.isnot(None),
                AnnotationData.labels != ''
            )
        ).all()
        
        # Count occurrences of each label
        label_counts = {}
        for annotation in annotations:
            if annotation.labels:
                labels = [label.strip() for label in annotation.labels.split(',')]
                for label in labels:
                    if label:
                        label_counts[label] = label_counts.get(label, 0) + 1
        
        # Convert to schema objects and sort by count
        label_stats = [
            schemas.LabelStats(label=label, count=count)
            for label, count in label_counts.items()
        ]
        
        return sorted(label_stats, key=lambda x: x.count, reverse=True) 