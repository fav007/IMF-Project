from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from ..database import get_db
from ..services.document_service import DocumentService
from ..schemas import DocumentResponse, DocumentList

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    bsc_number: str,
    category: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document."""
    service = DocumentService(db)
    return await service.upload_document(bsc_number, category, file)

@router.get("/list", response_model=List[DocumentList])
def list_documents(db: Session = Depends(get_db)):
    """List all documents."""
    service = DocumentService(db)
    return service.list_documents()

@router.get("/search", response_model=List[DocumentList])
def search_documents(
    bsc_number: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search documents by BSC number and/or category."""
    service = DocumentService(db)
    return service.search_documents(bsc_number, category)

@router.get("/download/{doc_uuid}")
def download_document(doc_uuid: str, db: Session = Depends(get_db)):
    """Download a document."""
    service = DocumentService(db)
    file_path, extension = service.get_document_path(doc_uuid)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=f"{doc_uuid}{extension}",
        media_type="application/octet-stream"
    ) 