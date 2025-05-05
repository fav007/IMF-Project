import os
import hashlib
import uuid
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
import io
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple

from ..models import Document, FileContent
from ..schemas import DocumentResponse, DocumentList
from ..config import settings

class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_sha256(self, file_content: bytes) -> str:
        """Calculate SHA256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()

    def convert_to_png(self, file_content: bytes, filename: str) -> List[bytes]:
        """Convert document to PNG pages."""
        pages = []
        if filename.lower().endswith(('.jpg', '.jpeg')):
            img = Image.open(io.BytesIO(file_content))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            pages.append(img_byte_arr.getvalue())
        else:  # PDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                pages.append(img_byte_arr.getvalue())
        return pages

    def format_filesize(self, size_mb: float) -> str:
        """Format file size with Mo suffix."""
        return f"{size_mb:.2f} Mo"

    async def upload_document(
        self, bsc_number: str, category: str, file: UploadFile
    ) -> DocumentResponse:
        """Upload a document with deduplication support."""
        if not any(file.filename.lower().endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
            raise HTTPException(status_code=400, detail="Invalid file type")

        file_content = await file.read()
        sha256_hash = self.calculate_sha256(file_content)
        
        # Check for existing content
        existing_content = self.db.query(FileContent).filter(FileContent.sha256 == sha256_hash).first()
        
        if existing_content:
            existing_content.reference_count += 1
            self.db.commit()
            
            document = Document(
                uuid=str(uuid.uuid4()),
                bsc_number=bsc_number,
                category=category,
                page_number=len(self.convert_to_png(file_content, file.filename)),
                filename=file.filename,
                filesize=len(file_content) / (1024 * 1024),
                upload_datetime=datetime.now(),
                sha256=sha256_hash
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            return DocumentResponse(
                uuid=document.uuid,
                bsc_number=document.bsc_number,
                category=document.category,
                filesize=self.format_filesize(document.filesize),
                message="Document uploaded successfully (deduplicated)"
            )
        
        # Create new document and content
        doc_uuid = str(uuid.uuid4())
        doc_dir = os.path.join(settings.UPLOAD_DIR, doc_uuid)
        os.makedirs(doc_dir, exist_ok=True)
        
        original_file_path = os.path.join(doc_dir, "original")
        with open(original_file_path, "wb") as f:
            f.write(file_content)
        
        file_content_record = FileContent(
            sha256=sha256_hash,
            file_path=original_file_path,
            reference_count=1
        )
        self.db.add(file_content_record)
        self.db.commit()
        
        document = Document(
            uuid=doc_uuid,
            bsc_number=bsc_number,
            category=category,
            page_number=len(self.convert_to_png(file_content, file.filename)),
            filename=file.filename,
            filesize=len(file_content) / (1024 * 1024),
            upload_datetime=datetime.now(),
            sha256=sha256_hash
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return DocumentResponse(
            uuid=document.uuid,
            bsc_number=document.bsc_number,
            category=document.category,
            filesize=self.format_filesize(document.filesize),
            message="Document uploaded successfully"
        )

    def list_documents(self) -> List[DocumentList]:
        """List all documents."""
        documents = self.db.query(Document).all()
        return [
            DocumentList(
                uuid=doc.uuid,
                bsc_number=doc.bsc_number,
                category=doc.category,
                page_number=doc.page_number,
                filesize=self.format_filesize(doc.filesize),
                upload_datetime=doc.upload_datetime
            )
            for doc in documents
        ]

    def search_documents(
        self, bsc_number: str = None, category: str = None
    ) -> List[DocumentList]:
        """Search documents by BSC number and/or category."""
        query = self.db.query(Document)
        
        if bsc_number:
            query = query.filter(Document.bsc_number == bsc_number)
        if category:
            query = query.filter(Document.category == category)
        
        documents = query.all()
        return [
            DocumentList(
                uuid=doc.uuid,
                bsc_number=doc.bsc_number,
                category=doc.category,
                page_number=doc.page_number,
                filesize=self.format_filesize(doc.filesize),
                upload_datetime=doc.upload_datetime
            )
            for doc in documents
        ]

    def get_document_path(self, doc_uuid: str) -> Tuple[str, str]:
        """Get document file path and extension."""
        document = self.db.query(Document).filter(Document.uuid == doc_uuid).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_content = self.db.query(FileContent).filter(FileContent.sha256 == document.sha256).first()
        if not file_content:
            raise HTTPException(status_code=404, detail="File content not found")
        
        if not os.path.exists(file_content.file_path):
            raise HTTPException(status_code=404, detail=f"File not found at path: {file_content.file_path}")
        
        return file_content.file_path, os.path.splitext(document.filename)[1].lower() 