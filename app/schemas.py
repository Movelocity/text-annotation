"""
文本标注 API 的 Pydantic schemas。

本模块定义了以下请求和响应模型：
- 标注数据操作
- 标签管理
- 数据导入操作
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnnotationDataBase(BaseModel):
    """标注数据的基础 schema。"""
    text: str = Field(..., description="文本内容")
    labels: Optional[str] = Field(None, description="逗号分隔的标签")


class AnnotationDataCreate(AnnotationDataBase):
    """创建新标注数据的 schema。"""
    pass


class AnnotationDataUpdate(BaseModel):
    """更新标注数据的 schema。"""
    labels: Optional[str] = Field(None, description="逗号分隔的标签")


class AnnotationDataResponse(AnnotationDataBase):
    """标注数据响应的 schema。"""
    id: int = Field(..., description="唯一标识符")
    
    class Config:
        from_attributes = True


class AnnotationDataList(BaseModel):
    """分页标注数据列表的 schema。"""
    items: List[AnnotationDataResponse]
    total: int = Field(..., description="记录总数")
    page: int = Field(..., description="当前页码")
    per_page: int = Field(..., description="每页记录数")


class LabelBase(BaseModel):
    """标签的基础 schema。"""
    label: str = Field(..., description="标签字符串")


class LabelCreate(LabelBase):
    """创建新标签的 schema。"""
    id: Optional[int] = Field(None, description="可选的自定义 ID")


class LabelResponse(LabelBase):
    """标签响应的 schema。"""
    id: int = Field(..., description="唯一标识符")
    
    class Config:
        from_attributes = True


class ImportStats(BaseModel):
    """导入操作统计的 schema。"""
    files_processed: int = Field(..., description="处理的文件数")
    records_imported: int = Field(..., description="导入的记录数")
    duplicates_merged: int = Field(..., description="合并的重复项数")


class ImportRequest(BaseModel):
    """导入请求的 schema。"""
    file_path: str = Field(..., description="要导入的文件路径")


class TextImportRequest(BaseModel):
    """文本导入请求的 schema。"""
    texts: List[str] = Field(..., description="要导入的文本列表")


class BulkLabelRequest(BaseModel):
    """批量标注请求的 schema。"""
    text_ids: List[int] = Field(..., description="要标注的文本 ID 列表")
    labels: str = Field(..., description="要应用的逗号分隔标签")


class SearchRequest(BaseModel):
    """文本搜索请求的 schema。"""
    query: Optional[str] = Field(None, description="文本搜索查询")
    labels: Optional[str] = Field(None, description="要过滤的逗号分隔标签")
    unlabeled_only: bool = Field(False, description="仅返回未标注文本")
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(50, description="每页记录数", ge=1, le=1000)


class LabelStats(BaseModel):
    """标签统计的 schema。"""
    label: str = Field(..., description="标签名称")
    count: int = Field(..., description="带有此标签的文本数")


class SystemStats(BaseModel):
    """系统统计的 schema。"""
    total_texts: int = Field(..., description="总文本数")
    labeled_texts: int = Field(..., description="已标注文本数")
    unlabeled_texts: int = Field(..., description="未标注文本数")
    total_labels: int = Field(..., description="总唯一标签数")
    label_statistics: List[LabelStats] = Field(..., description="每个标签的统计") 