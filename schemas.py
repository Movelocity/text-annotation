"""
Pydantic schemas for the text annotation API.

This module defines request and response models for:
- Annotation data operations
- Label management
- Data import operations
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnnotationDataBase(BaseModel):
    """Base schema for annotation data."""
    text: str = Field(..., description="The text content")
    labels: Optional[str] = Field(None, description="Comma-separated labels")


class AnnotationDataCreate(AnnotationDataBase):
    """Schema for creating new annotation data."""
    pass


class AnnotationDataUpdate(BaseModel):
    """Schema for updating annotation data."""
    labels: Optional[str] = Field(None, description="Comma-separated labels")


class AnnotationDataResponse(AnnotationDataBase):
    """Schema for annotation data response."""
    id: int = Field(..., description="Unique identifier")
    
    class Config:
        from_attributes = True


class AnnotationDataList(BaseModel):
    """Schema for paginated annotation data list."""
    items: List[AnnotationDataResponse]
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")


class LabelBase(BaseModel):
    """Base schema for labels."""
    label: str = Field(..., description="The label string")


class LabelCreate(LabelBase):
    """Schema for creating new labels."""
    id: Optional[int] = Field(None, description="Optional custom ID")


class LabelResponse(LabelBase):
    """Schema for label response."""
    id: int = Field(..., description="Unique identifier")
    
    class Config:
        from_attributes = True


class ImportStats(BaseModel):
    """Schema for import operation statistics."""
    files_processed: int = Field(..., description="Number of files processed")
    records_imported: int = Field(..., description="Number of records imported")
    duplicates_merged: int = Field(..., description="Number of duplicates merged")


class ImportRequest(BaseModel):
    """Schema for import request."""
    file_path: str = Field(..., description="Path to the file to import")


class TextImportRequest(BaseModel):
    """Schema for text import request."""
    texts: List[str] = Field(..., description="List of texts to import")


class BulkLabelRequest(BaseModel):
    """Schema for bulk labeling request."""
    text_ids: List[int] = Field(..., description="List of text IDs to label")
    labels: str = Field(..., description="Comma-separated labels to apply")


class SearchRequest(BaseModel):
    """Schema for text search request."""
    query: Optional[str] = Field(None, description="Text search query")
    labels: Optional[str] = Field(None, description="Comma-separated labels to filter by")
    unlabeled_only: bool = Field(False, description="Only return unlabeled texts")
    page: int = Field(1, description="Page number", ge=1)
    per_page: int = Field(50, description="Records per page", ge=1, le=1000)


class LabelStats(BaseModel):
    """Schema for label statistics."""
    label: str = Field(..., description="Label name")
    count: int = Field(..., description="Number of texts with this label")


class SystemStats(BaseModel):
    """Schema for system statistics."""
    total_texts: int = Field(..., description="Total number of texts")
    labeled_texts: int = Field(..., description="Number of labeled texts")
    unlabeled_texts: int = Field(..., description="Number of unlabeled texts")
    total_labels: int = Field(..., description="Total number of unique labels")
    label_stats: List[LabelStats] = Field(..., description="Statistics per label") 