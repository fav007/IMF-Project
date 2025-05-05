from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class FileContent(Base):
    """Represents the actual content of a file, with deduplication support."""
    __tablename__ = "file_contents"

    sha256 = Column(String, primary_key=True, index=True, comment="SHA256 hash of the file content")
    file_path = Column(String, unique=True, nullable=False, comment="Path to the stored file")
    reference_count = Column(Integer, default=1, comment="Number of documents referencing this content")

    documents = relationship("Document", back_populates="file_content")

class Document(Base):
    """Represents a document with its metadata and reference to file content."""
    __tablename__ = "documents"

    uuid = Column(String, primary_key=True, index=True, comment="Unique identifier for the document")
    bsc_number = Column(String, index=True, nullable=False, comment="BSC number associated with the document")
    category = Column(String, nullable=False, comment="Document category (DED,INV,BIL,PKL,DAU,DOM,BSC,OTH)")
    page_number = Column(Integer, nullable=False, comment="Number of pages in the document")
    filename = Column(String, nullable=False, comment="Original filename")
    filesize = Column(Float, nullable=False, comment="File size in megabytes")
    upload_datetime = Column(DateTime, nullable=False, comment="Timestamp of upload", default=datetime.now)
    sha256 = Column(String, ForeignKey("file_contents.sha256"), index=True, nullable=False, comment="Reference to file content")
    
    # Relationship
    file_content = relationship("FileContent", back_populates="documents") 