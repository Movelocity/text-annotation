"""
文本标注系统的数据导入工具。

本模块提供以下功能：
- 从目录结构导入旧的标注数据
- 导入新的未标注文本数据
- 合并重复文本并组合标签
"""

import os
import yaml
from typing import Dict, List, Set
from sqlalchemy.orm import Session
from app.models import AnnotationData, Label, SessionLocal, create_tables
from tqdm import tqdm

class DataImporter:
    """处理导入和处理标注数据。"""
    
    def __init__(self, db_session: Session = None):
        """
        初始化数据导入器。
        
        Args:
            db_session: 可选的数据库会话，如果未提供则创建新的
        """
        self.db = db_session or SessionLocal()
    
    def import_old_data(self, old_data_path: str) -> Dict[str, int]:
        """
        从目录结构导入旧的标注数据。
        
        处理 old-data/**/<label>.txt 文件，其中每行是一个记录。
        合并相同记录并用逗号分隔组合标签。
        
        Args:
            old_data_path: old-data 目录的路径
            
        Returns:
            包含导入统计信息的字典
        """
        text_labels_map = {}  # text -> set of labels
        stats = {"files_processed": 0, "records_imported": 0, "duplicates_merged": 0}
        
        # 遍历所有子目录
        for root, dirs, files in os.walk(old_data_path):
            for file in files:
                if file.endswith('.txt') and file != 'label_config.yaml':
                    label_name = os.path.splitext(file)[0]
                    file_path = os.path.join(root, file)
                    
                    print(f"正在处理 {file_path}，标签: {label_name}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            text = line.strip()
                            if not text: 
                                continue # 跳过空行
                            if text in text_labels_map:
                                text_labels_map[text].add(label_name)
                                stats["duplicates_merged"] += 1
                            else:
                                text_labels_map[text] = {label_name}
                    
                    stats["files_processed"] += 1
        
        # 将数据插入数据库
        for text, labels in tqdm(text_labels_map.items(), desc="数据插入数据库", total=len(text_labels_map)):
            labels_str = ','.join(sorted(labels))  # 排序以保持一致性
            
            # 检查文本是否已存在
            existing = self.db.query(AnnotationData).filter(AnnotationData.text == text).first()
            if existing:
                # 如果标签不同则更新
                if existing.labels != labels_str:
                    existing.labels = labels_str
            else:
                annotation = AnnotationData(text=text, labels=labels_str)
                self.db.add(annotation)
                stats["records_imported"] += 1
        
        self.db.commit()
        return stats
    
    def import_label_config(self, config_path: str) -> int:
        """
        从 YAML 文件导入标签配置。
        
        Args:
            config_path: label_config.yaml 文件的路径
            
        Returns:
            导入的标签数量
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        labels_imported = 0
        if 'id2label' in config:
            for label_id, label_name in config['id2label'].items():
                # 检查标签是否已存在
                existing = self.db.query(Label).filter(Label.id == int(label_id)).first()
                if not existing:
                    label = Label(id=int(label_id), label=label_name, description=None)
                    self.db.add(label)
                    labels_imported += 1
        
        self.db.commit()
        return labels_imported
    
    def import_text_file(self, file_path: str) -> int:
        """
        从文件导入新的未标注文本数据。
        
        文件中每行被视为一个单独的文本记录。
        
        Args:
            file_path: 包含未标注数据的文本文件路径
            
        Returns:
            导入的新记录数量
        """
        records_imported = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                text = line.strip()
                if text:  # 跳过空行
                    # 检查文本是否已存在
                    existing = self.db.query(AnnotationData).filter(AnnotationData.text == text).first()
                    if not existing:
                        annotation = AnnotationData(text=text, labels='')
                        self.db.add(annotation)
                        records_imported += 1
        
        self.db.commit()
        return records_imported
    
    def get_all_unique_labels(self) -> Set[str]:
        """
        从标注数据中获取所有唯一标签。
        
        Returns:
            所有唯一标签名称的集合
        """
        all_labels = set()
        annotations = self.db.query(AnnotationData).filter(AnnotationData.labels.isnot(None)).all()
        
        for annotation in annotations:
            if annotation.labels:
                labels = annotation.labels.split(',')
                all_labels.update([label.strip() for label in labels])
        
        return all_labels
    
    def sync_labels_from_annotations(self) -> int:
        """
        将标签表与标注数据中找到的唯一标签同步。
        
        Returns:
            添加的新标签数量
        """
        unique_labels = self.get_all_unique_labels()
        new_labels_count = 0
        
        # 获取现有的最大标签 ID
        max_id = self.db.query(Label).order_by(Label.id.desc()).first()
        next_id = (max_id.id + 1) if max_id else 0
        
        for label_name in unique_labels:
            existing = self.db.query(Label).filter(Label.label == label_name).first()
            if not existing:
                label = Label(id=next_id, label=label_name, description=None)
                self.db.add(label)
                next_id += 1
                new_labels_count += 1
        
        self.db.commit()
        return new_labels_count
    
    def __del__(self):
        """清理数据库会话。"""
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """运行数据导入的主函数。"""
    # 如果表不存在则创建
    create_tables()
    
    importer = DataImporter()
    
    # 从父目录导入旧数据
    old_data_path = "./archive/old-data"
    if os.path.exists(old_data_path):
        print("正在导入旧的标注数据...")
        stats = importer.import_old_data(old_data_path)
        print(f"导入完成: {stats}")
        
        # 导入标签配置
        config_path = os.path.join(old_data_path, "label_config.yaml")
        if os.path.exists(config_path):
            print("正在导入标签配置...")
            labels_count = importer.import_label_config(config_path)
            print(f"从配置导入了 {labels_count} 个标签")
        
        # 同步任何缺失的标签
        print("正在从标注数据同步标签...")
        new_labels = importer.sync_labels_from_annotations()
        print(f"向标签表添加了 {new_labels} 个新标签")
    else:
        print(f"旧数据路径 {old_data_path} 未找到")


if __name__ == "__main__":
    main() 