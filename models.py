"""
文本标注系统的数据库模型。

本模块定义了以下 SQLAlchemy 模型：
- AnnotationData: 存储带有关联标签的文本（无重复）
- Label: 存储带有 id 和标签字符串的标签信息
"""

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class AnnotationData(Base):
    """
    存储文本标注数据的模型。
    
    Attributes:
        id: 主键（自动生成）
        text: 文本内容（不允许重复）
        labels: 与文本关联的标签的逗号分隔字符串
    """
    __tablename__ = "annotation_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False, unique=True)  # 不允许重复文本
    labels = Column(String, nullable=True)  # 逗号分隔的标签


class Label(Base):
    """
    标签管理的模型。
    
    Attributes:
        id: 标签的唯一标识符
        label: 标签字符串
    """
    __tablename__ = "labels"
    
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False, unique=True)


# 数据库设置
DATABASE_URL = "sqlite:///./annotation.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """创建所有数据库表。"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取 FastAPI 的数据库会话依赖。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 