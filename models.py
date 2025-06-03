"""
Database models for the text annotation system.

This module defines the SQLAlchemy models for:
- AnnotationData: Stores text with associated labels (no duplicates)
- Label: Stores label information with id and label string
"""

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class AnnotationData(Base):
    """
    Model for storing text annotation data.
    
    Attributes:
        id: Primary key (auto-generated)
        text: The text content (no duplicates allowed)
        labels: Comma-separated string of labels associated with the text
    """
    __tablename__ = "annotation_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False, unique=True)  # No duplicate text allowed
    labels = Column(String, nullable=True)  # Comma-separated labels


class Label(Base):
    """
    Model for label management.
    
    Attributes:
        id: Unique identifier for the label
        label: The label string
    """
    __tablename__ = "labels"
    
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False, unique=True)


# Database setup
DATABASE_URL = "sqlite:///./annotation.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 