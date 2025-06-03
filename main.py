"""
FastAPI application for text annotation system.

This module provides REST API endpoints for:
- Annotation data CRUD operations
- Label management
- Data import and export
- Search and filtering
- Statistics and analytics
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from models import get_db, create_tables
from services import AnnotationService, LabelService, StatisticsService
from data_import import DataImporter
import schemas

# Create FastAPI application
app = FastAPI(
    title="Text Annotation API",
    description="Backend API for text annotation and labeling system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()


# Annotation Data Endpoints
@app.post("/annotations/", response_model=schemas.AnnotationDataResponse, status_code=status.HTTP_201_CREATED)
def create_annotation(
    annotation: schemas.AnnotationDataCreate,
    db: Session = Depends(get_db)
):
    """
    Create new annotation data.
    
    Args:
        annotation: Annotation data to create
        db: Database session
        
    Returns:
        Created annotation data
        
    Raises:
        HTTPException: If text already exists
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
    Get annotation data by ID.
    
    Args:
        annotation_id: ID of the annotation
        db: Database session
        
    Returns:
        Annotation data
        
    Raises:
        HTTPException: If annotation not found
    """
    service = AnnotationService(db)
    annotation = service.get_annotation(annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


@app.put("/annotations/{annotation_id}", response_model=schemas.AnnotationDataResponse)
def update_annotation(
    annotation_id: int,
    update_data: schemas.AnnotationDataUpdate,
    db: Session = Depends(get_db)
):
    """
    Update annotation data.
    
    Args:
        annotation_id: ID of the annotation to update
        update_data: Data to update
        db: Database session
        
    Returns:
        Updated annotation data
        
    Raises:
        HTTPException: If annotation not found
    """
    service = AnnotationService(db)
    annotation = service.update_annotation(annotation_id, update_data)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


@app.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete annotation data.
    
    Args:
        annotation_id: ID of the annotation to delete
        db: Database session
        
    Raises:
        HTTPException: If annotation not found
    """
    service = AnnotationService(db)
    if not service.delete_annotation(annotation_id):
        raise HTTPException(status_code=404, detail="Annotation not found")


@app.post("/annotations/search", response_model=schemas.AnnotationDataList)
def search_annotations(
    search_request: schemas.SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search and filter annotation data.
    
    Args:
        search_request: Search parameters
        db: Database session
        
    Returns:
        Paginated list of annotation data
    """
    service = AnnotationService(db)
    return service.search_annotations(search_request)


@app.post("/annotations/bulk-label")
def bulk_label_annotations(
    bulk_request: schemas.BulkLabelRequest,
    db: Session = Depends(get_db)
):
    """
    Apply labels to multiple texts.
    
    Args:
        bulk_request: Bulk labeling request
        db: Database session
        
    Returns:
        Number of texts updated
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
    Import multiple texts as unlabeled data.
    
    Args:
        import_request: Text import request
        db: Database session
        
    Returns:
        Number of texts imported
    """
    service = AnnotationService(db)
    imported_count = service.import_texts(import_request)
    return {"imported_count": imported_count}


# Label Management Endpoints
@app.post("/labels/", response_model=schemas.LabelResponse, status_code=status.HTTP_201_CREATED)
def create_label(
    label: schemas.LabelCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new label.
    
    Args:
        label: Label data to create
        db: Database session
        
    Returns:
        Created label
        
    Raises:
        HTTPException: If label already exists
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
    Get all labels.
    
    Args:
        db: Database session
        
    Returns:
        List of all labels
    """
    service = LabelService(db)
    return service.get_all_labels()


@app.get("/labels/{label_id}", response_model=schemas.LabelResponse)
def get_label(
    label_id: int,
    db: Session = Depends(get_db)
):
    """
    Get label by ID.
    
    Args:
        label_id: ID of the label
        db: Database session
        
    Returns:
        Label data
        
    Raises:
        HTTPException: If label not found
    """
    service = LabelService(db)
    label = service.get_label(label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    return label


@app.delete("/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(
    label_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a label.
    
    Args:
        label_id: ID of the label to delete
        db: Database session
        
    Raises:
        HTTPException: If label not found
    """
    service = LabelService(db)
    if not service.delete_label(label_id):
        raise HTTPException(status_code=404, detail="Label not found")


# Data Import Endpoints
@app.post("/import/old-data", response_model=schemas.ImportStats)
def import_old_data(
    old_data_path: str = "../old-data",
    db: Session = Depends(get_db)
):
    """
    Import old labeled data from directory structure.
    
    Args:
        old_data_path: Path to the old-data directory
        db: Database session
        
    Returns:
        Import statistics
        
    Raises:
        HTTPException: If path not found or import fails
    """
    if not os.path.exists(old_data_path):
        raise HTTPException(status_code=404, detail=f"Path {old_data_path} not found")
    
    try:
        importer = DataImporter(db)
        stats = importer.import_old_data(old_data_path)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@app.post("/import/label-config")
def import_label_config(
    config_path: str = "../old-data/label_config.yaml",
    db: Session = Depends(get_db)
):
    """
    Import label configuration from YAML file.
    
    Args:
        config_path: Path to the label_config.yaml file
        db: Database session
        
    Returns:
        Number of labels imported
        
    Raises:
        HTTPException: If file not found or import fails
    """
    if not os.path.exists(config_path):
        raise HTTPException(status_code=404, detail=f"Config file {config_path} not found")
    
    try:
        importer = DataImporter(db)
        labels_count = importer.import_label_config(config_path)
        return {"labels_imported": labels_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@app.post("/import/text-file")
def import_text_file(
    import_request: schemas.ImportRequest,
    db: Session = Depends(get_db)
):
    """
    Import new unlabeled text data from a file.
    
    Args:
        import_request: Import request with file path
        db: Database session
        
    Returns:
        Number of records imported
        
    Raises:
        HTTPException: If file not found or import fails
    """
    if not os.path.exists(import_request.file_path):
        raise HTTPException(status_code=404, detail=f"File {import_request.file_path} not found")
    
    try:
        importer = DataImporter(db)
        records_imported = importer.import_new_text_data(import_request.file_path)
        return {"records_imported": records_imported}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


# Statistics Endpoints
@app.get("/stats/system", response_model=schemas.SystemStats)
def get_system_stats(db: Session = Depends(get_db)):
    """
    Get overall system statistics.
    
    Args:
        db: Database session
        
    Returns:
        System statistics
    """
    service = StatisticsService(db)
    return service.get_system_stats()


# Health Check Endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy", "message": "Text annotation API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
