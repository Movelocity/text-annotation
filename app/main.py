"""
文本标注系统的 FastAPI 应用程序。

本模块提供以下 REST API 端点：
- 标注数据的 CRUD 操作
- 标签管理
- 数据导入和导出
- 搜索和过滤
- 统计和分析
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import logging

from .models import get_db, create_tables
from .services import AnnotationService, LabelService, StatisticsService
from scripts.data_import import DataImporter
from . import schemas

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用程序
app = FastAPI(
    title="文本标注 API",
    description="文本标注和标记系统的后端 API",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中需要适当配置
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库表。"""
    create_tables()


# 标注数据端点
@app.post("/annotations/", response_model=schemas.AnnotationDataResponse, status_code=status.HTTP_201_CREATED)
def create_annotation(
    annotation: schemas.AnnotationDataCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的标注数据。
    
    Args:
        annotation: 要创建的标注数据
        db: 数据库会话
        
    Returns:
        创建的标注数据
        
    Raises:
        HTTPException: 如果文本已存在
    """
    service = AnnotationService(db)
    try:
        result = service.create_annotation(annotation)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/annotations/{annotation_id}", response_model=schemas.AnnotationDataResponse)
def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db)
):
    """
    根据 ID 获取标注数据。
    
    Args:
        annotation_id: 标注的 ID
        db: 数据库会话
        
    Returns:
        标注数据
        
    Raises:
        HTTPException: 如果标注未找到
    """
    service = AnnotationService(db)
    annotation = service.get_annotation(annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="标注未找到")
    return annotation


@app.put("/annotations/{annotation_id}", response_model=schemas.AnnotationDataResponse)
def update_annotation(
    annotation_id: int,
    update_data: schemas.AnnotationDataUpdate,
    db: Session = Depends(get_db)
):
    """
    更新标注数据。
    
    Args:
        annotation_id: 要更新的标注 ID
        update_data: 要更新的数据
        db: 数据库会话
        
    Returns:
        更新后的标注数据
        
    Raises:
        HTTPException: 如果标注未找到
    """
    service = AnnotationService(db)
    annotation = service.update_annotation(annotation_id, update_data)
    if not annotation:
        raise HTTPException(status_code=404, detail="标注未找到")
    return annotation


@app.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db)
):
    """
    删除标注数据。
    
    Args:
        annotation_id: 要删除的标注 ID
        db: 数据库会话
        
    Raises:
        HTTPException: 如果标注未找到
    """
    service = AnnotationService(db)
    if not service.delete_annotation(annotation_id):
        raise HTTPException(status_code=404, detail="标注未找到")


@app.post("/annotations/search", response_model=schemas.AnnotationDataList)
def search_annotations(
    search_request: schemas.SearchRequest,
    db: Session = Depends(get_db)
):
    """
    搜索和过滤标注数据。
    
    Args:
        search_request: 搜索参数
        db: 数据库会话
        
    Returns:
        分页的标注数据列表
    """
    service = AnnotationService(db)
    return service.search_annotations(search_request)


@app.post("/annotations/bulk-label")
def bulk_label_annotations(
    bulk_request: schemas.BulkLabelRequest,
    db: Session = Depends(get_db)
):
    """
    为多个文本应用标签。
    
    Args:
        bulk_request: 批量标注请求
        db: 数据库会话
        
    Returns:
        更新的文本数量
    """
    service = AnnotationService(db)
    updated_count = service.bulk_label(bulk_request)
    return {"updated_count": updated_count}


@app.post("/annotations/import-texts")
def import_texts(
    import_request: schemas.TextImportRequest,
    db: Session = Depends(get_db)
):
    """
    导入多个文本作为未标注数据。
    
    Args:
        import_request: 文本导入请求
        db: 数据库会话
        
    Returns:
        导入的文本数量
    """
    service = AnnotationService(db)
    imported_count = service.import_texts(import_request)
    return {"imported_count": imported_count}


# 标签端点
@app.post("/labels/", response_model=schemas.LabelResponse, status_code=status.HTTP_201_CREATED)
def create_label(
    label: schemas.LabelCreate,
    db: Session = Depends(get_db)
):
    """
    创建新标签。
    
    Args:
        label: 要创建的标签
        db: 数据库会话
        
    Returns:
        创建的标签
        
    Raises:
        HTTPException: 如果标签已存在
    """
    service = LabelService(db)
    try:
        result = service.create_label(label)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/labels/", response_model=List[schemas.LabelResponse])
def get_all_labels(db: Session = Depends(get_db)):
    """
    获取所有标签。
    
    Args:
        db: 数据库会话
        
    Returns:
        标签列表
    """
    service = LabelService(db)
    return service.get_all_labels()


@app.get("/labels/{label_id}", response_model=schemas.LabelResponse)
def get_label(
    label_id: int,
    db: Session = Depends(get_db)
):
    """
    根据 ID 获取标签。
    
    Args:
        label_id: 标签 ID
        db: 数据库会话
        
    Returns:
        标签数据
        
    Raises:
        HTTPException: 如果标签未找到
    """
    service = LabelService(db)
    label = service.get_label(label_id)
    if not label:
        raise HTTPException(status_code=404, detail="标签未找到")
    return label


@app.delete("/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(
    label_id: int,
    db: Session = Depends(get_db)
):
    """
    删除标签。
    
    Args:
        label_id: 要删除的标签 ID
        db: 数据库会话
        
    Raises:
        HTTPException: 如果标签未找到
    """
    service = LabelService(db)
    if not service.delete_label(label_id):
        raise HTTPException(status_code=404, detail="标签未找到")


# 数据导入端点
@app.post("/import/old-data", response_model=schemas.ImportStats)
def import_old_data(
    old_data_path: str = "../old-data",
    db: Session = Depends(get_db)
):
    """
    导入旧的标注数据。
    
    Args:
        old_data_path: 旧数据路径
        db: 数据库会话
        
    Returns:
        导入统计信息
        
    Raises:
        HTTPException: 如果路径未找到或导入失败
    """
    if not os.path.exists(old_data_path):
        raise HTTPException(status_code=404, detail=f"路径 {old_data_path} 未找到")
    
    try:
        importer = DataImporter()
        stats = importer.import_old_data(old_data_path, db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.post("/import/label-config")
def import_label_config(
    config_path: str = "../old-data/label_config.yaml",
    db: Session = Depends(get_db)
):
    """
    导入标签配置。
    
    Args:
        config_path: 配置文件路径
        db: 数据库会话
        
    Returns:
        导入的标签数量
        
    Raises:
        HTTPException: 如果文件未找到或导入失败
    """
    if not os.path.exists(config_path):
        raise HTTPException(status_code=404, detail=f"配置文件 {config_path} 未找到")
    
    try:
        importer = DataImporter()
        labels_count = importer.import_label_config(config_path, db)
        return {"imported_labels": labels_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.post("/import/text-file")
def import_text_file(
    import_request: schemas.ImportRequest,
    db: Session = Depends(get_db)
):
    """
    导入文本文件（高性能批量版本 + 进度跟踪）。
    
    Args:
        import_request: 导入请求
        db: 数据库会话
        
    Returns:
        导入的文本数量和相关统计信息
        
    Raises:
        HTTPException: 如果文件未找到或导入失败
    """
    file_path = import_request.file_path
    
    # 文件存在性检查
    if not os.path.exists(file_path):
        logger.error(f"文件未找到: {file_path}")
        raise HTTPException(status_code=404, detail=f"文件 {file_path} 未找到")
    
    # 文件权限检查
    if not os.access(file_path, os.R_OK):
        logger.error(f"文件无读取权限: {file_path}")
        raise HTTPException(status_code=403, detail=f"文件 {file_path} 无读取权限")
    
    # 文件大小检查 (可选，防止过大文件)
    try:
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB 限制
            logger.warning(f"文件过大: {file_path}, 大小: {file_size} bytes")
            raise HTTPException(status_code=413, detail=f"文件过大，请确保文件小于 100MB")
    except OSError as e:
        logger.error(f"获取文件大小失败: {file_path}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="无法访问文件")
    
    try:
        logger.info(f"开始导入文件: {file_path}")
        service = AnnotationService(db)
        imported_count = service.import_text_file(file_path)
        
        logger.info(f"文件导入完成: {file_path}, 导入记录数: {imported_count}")
        return {
            "imported_count": imported_count,
            "file_path": file_path,
            "file_size": file_size,
            "status": "success"
        }
        
    except FileNotFoundError as e:
        logger.error(f"文件读取时未找到: {file_path}, 错误: {str(e)}")
        raise HTTPException(status_code=404, detail=f"文件读取失败，文件可能已被移动或删除")
        
    except PermissionError as e:
        logger.error(f"文件权限错误: {file_path}, 错误: {str(e)}")
        raise HTTPException(status_code=403, detail=f"文件权限不足: {str(e)}")
        
    except UnicodeDecodeError as e:
        logger.error(f"文件编码错误: {file_path}, 错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"文件编码错误，请确保文件为 UTF-8 编码")
        
    except Exception as e:
        logger.error(f"导入失败: {file_path}, 错误: {str(e)}", exc_info=True)
        # 回滚数据库事务（如果需要）
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


# 统计端点
@app.get("/stats", response_model=schemas.SystemStats)
def get_stats_alias(db: Session = Depends(get_db)):
    """
    获取系统统计信息（别名）。
    
    Args:
        db: 数据库会话
        
    Returns:
        系统统计数据
    """
    service = StatisticsService(db)
    return service.get_system_stats()


@app.get("/stats/system", response_model=schemas.SystemStats)
def get_system_stats(db: Session = Depends(get_db)):
    """
    获取系统统计信息。
    
    Args:
        db: 数据库会话
        
    Returns:
        系统统计数据
    """
    service = StatisticsService(db)
    return service.get_system_stats()


# 健康检查端点
@app.get("/health")
def health_check():
    """健康检查端点。"""
    return {"status": "healthy", "message": "文本标注 API 正在运行"}


def main():
    """启动服务器的主函数。"""
    import uvicorn
    from .config import HOST, PORT
    
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        # reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
