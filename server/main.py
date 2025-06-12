"""
文本标注系统的 FastAPI 应用程序。

本模块提供以下 REST API 端点：
- 标注数据的 CRUD 操作
- 标签管理
- 数据导入和导出
- 搜索和过滤
- 统计和分析
"""

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import os
import logging

from .models import get_db, create_tables
from .services import AnnotationService, LabelService, StatisticsService
from .generation_service import generation_service
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

# 挂载静态文件目录
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "dist")
if os.path.exists(static_dir):
    # 挂载静态资源目录
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    # 挂载其他静态文件（如 vite.svg）
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"静态文件目录已挂载: {static_dir}")
else:
    logger.warning(f"静态文件目录不存在: {static_dir}")


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库表。"""
    create_tables()


# 前端页面路由
@app.get("/")
async def serve_frontend():
    """
    提供前端页面。
    
    Returns:
        前端 index.html 文件
    """
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "dist")
    index_file = os.path.join(static_dir, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        raise HTTPException(status_code=404, detail="前端文件未找到，请先构建前端项目")


@app.get("/vite.svg")
async def serve_vite_svg():
    """
    提供 vite.svg 文件。
    
    Returns:
        vite.svg 文件
    """
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "dist")
    vite_file = os.path.join(static_dir, "vite.svg")
    
    if os.path.exists(vite_file):
        return FileResponse(vite_file)
    else:
        raise HTTPException(status_code=404, detail="vite.svg 文件未找到")


@app.get("/favicon.ico")
async def serve_favicon():
    """
    提供 favicon.ico 文件。
    
    Returns:
        favicon.ico 文件
    """
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "dist")
    favicon_file = os.path.join(static_dir, "favicon.ico")
    
    if os.path.exists(favicon_file):
        return FileResponse(favicon_file, media_type="image/x-icon")
    else:
        logger.warning(f"favicon.ico 文件不存在: {favicon_file}")
        # 如果 favicon.ico 不存在，返回 204 No Content 而不是 404
        # 这样浏览器不会在控制台显示错误信息
        return Response(
            content="",
            status_code=204,
            headers={"Content-Length": "0"}
        )


@app.get("/pages/{path:path}")
async def serve_spa_pages(path: str):
    """
    将所有 /pages/* 路径转发给 SPA 前端处理。
    
    这个路由捕获所有以 /pages/ 开头的路径，并返回 index.html，
    让前端路由器（如 Vue Router）来处理页面导航。
    
    Args:
        path: 页面路径（将被前端路由器处理）
        
    Returns:
        前端 index.html 文件，让 SPA 处理路由
    """
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "dist")
    index_file = os.path.join(static_dir, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        raise HTTPException(status_code=404, detail="前端文件未找到，请先构建前端项目")


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


@app.post("/annotations/bulk-update-labels", response_model=schemas.BulkLabelUpdateResponse)
def bulk_update_labels(
    update_request: schemas.BulkLabelUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    批量更新标签（添加或删除）。
    
    支持两种操作方式：
    1. 通过搜索条件筛选数据后批量更新
    2. 通过指定文本ID列表批量更新
    
    支持两种标签操作：
    1. 添加标签：将新标签添加到现有标签中（不删除现有标签）
    2. 删除标签：从现有标签中删除指定标签（保留其他标签）
    
    Args:
        update_request: 批量标签更新请求
        db: 数据库会话
        
    Returns:
        更新操作的结果，包含更新的记录数量和操作描述
        
    Raises:
        HTTPException: 如果请求参数无效
    """
    service = AnnotationService(db)
    try:
        result = service.bulk_update_labels(update_request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量更新标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量更新失败: {str(e)}")


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


@app.put("/labels/{label_id}", response_model=schemas.LabelResponse)
def update_label(
    label_id: int,
    label_data: schemas.LabelUpdate,
    db: Session = Depends(get_db)
):
    """
    更新标签。
    
    Args:
        label_id: 要更新的标签 ID
        label_data: 更新的标签数据
        db: 数据库会话
        
    Returns:
        更新后的标签数据
        
    Raises:
        HTTPException: 如果标签未找到或标签字符串重复
    """
    service = LabelService(db)
    try:
        label = service.update_label(label_id, label_data)
        if not label:
            raise HTTPException(status_code=404, detail="标签未找到")
        return label
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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


# 数据生成端点
@app.post("/generate/start")
async def start_generation(request: schemas.GenerateRequest):
    """
    启动数据生成任务。
    
    Args:
        request: 生成请求参数
        
    Returns:
        任务ID和初始状态
        
    Raises:
        HTTPException: 如果请求参数无效
    """
    try:
        # 创建生成任务
        task_id = generation_service.create_task(request)
        
        return {
            "task_id": task_id,
            "status": "created",
            "message": "生成任务已创建，请使用task_id获取流式更新"
        }
        
    except Exception as e:
        logger.error(f"创建生成任务失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/generate/stream/{task_id}")
async def stream_generation(task_id: str):
    """
    获取生成任务的流式更新。
    
    Args:
        task_id: 任务ID
        
    Returns:
        Server-Sent Events流
        
    Raises:
        HTTPException: 如果任务不存在
    """
    task = generation_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return StreamingResponse(
        generation_service.generate_stream(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.post("/generate/cancel/{task_id}")
async def cancel_generation(task_id: str):
    """
    取消生成任务。
    
    Args:
        task_id: 任务ID
        
    Returns:
        取消结果
        
    Raises:
        HTTPException: 如果任务不存在
    """
    success = generation_service.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {"message": "任务已取消"}


@app.get("/generate/status/{task_id}", response_model=schemas.GenerateStatus)
async def get_generation_status(task_id: str):
    """
    获取生成任务状态。
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态
        
    Raises:
        HTTPException: 如果任务不存在
    """
    task = generation_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task.get_status()


@app.get("/generate/results/{task_id}")
async def get_generation_results(task_id: str):
    """
    获取生成任务的结果。
    
    Args:
        task_id: 任务ID
        
    Returns:
        生成的文本列表
        
    Raises:
        HTTPException: 如果任务不存在
    """
    task = generation_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task_id,
        "status": task.status,
        "generated_count": len(task.generated_texts),
        "texts": [text.model_dump() for text in task.generated_texts]
    }


# 健康检查端点
@app.get("/health")
def health_check():
    """健康检查端点。"""
    return {"status": "healthy", "message": "文本标注 API 正在运行"}


def main():
    """启动服务器的主函数。"""
    import uvicorn
    from .config import HOST, PORT
    print(f"访问: http://localhost:{PORT}")
    uvicorn.run(
        "server.main:app",
        host=HOST,
        port=PORT,
        # reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
