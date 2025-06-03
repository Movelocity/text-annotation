"""
Data import utilities for the text annotation system.

This module provides functions to:
- Import old labeled data from directory structure
- Import new unlabeled text data
- Merge duplicate texts with combined labels
"""

import os
import yaml
from typing import Dict, List, Set
from sqlalchemy.orm import Session
from models import AnnotationData, Label, SessionLocal, create_tables


class DataImporter:
    """Handles importing and processing annotation data."""
    
    def __init__(self, db_session: Session = None):
        """
        Initialize the data importer.
        
        Args:
            db_session: Optional database session, creates new one if not provided
        """
        self.db = db_session or SessionLocal()
    
    def import_old_data(self, old_data_path: str) -> Dict[str, int]:
        """
        Import old labeled data from directory structure.
        
        Processes old-data/**/<label>.txt files where each line is a record.
        Merges common records and combines labels separated by comma.
        
        Args:
            old_data_path: Path to the old-data directory
            
        Returns:
            Dictionary with import statistics
        """
        text_labels_map = {}  # text -> set of labels
        stats = {"files_processed": 0, "records_imported": 0, "duplicates_merged": 0}
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(old_data_path):
            for file in files:
                if file.endswith('.txt') and file != 'label_config.yaml':
                    label_name = os.path.splitext(file)[0]
                    file_path = os.path.join(root, file)
                    
                    print(f"Processing {file_path} with label: {label_name}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            text = line.strip()
                            if text:  # Skip empty lines
                                if text in text_labels_map:
                                    text_labels_map[text].add(label_name)
                                    stats["duplicates_merged"] += 1
                                else:
                                    text_labels_map[text] = {label_name}
                    
                    stats["files_processed"] += 1
        
        # Insert data into database
        for text, labels in text_labels_map.items():
            labels_str = ','.join(sorted(labels))  # Sort for consistency
            
            # Check if text already exists
            existing = self.db.query(AnnotationData).filter(AnnotationData.text == text).first()
            if existing:
                # Update labels if different
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
        Import label configuration from YAML file.
        
        Args:
            config_path: Path to the label_config.yaml file
            
        Returns:
            Number of labels imported
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        labels_imported = 0
        if 'id2label' in config:
            for label_id, label_name in config['id2label'].items():
                # Check if label already exists
                existing = self.db.query(Label).filter(Label.id == int(label_id)).first()
                if not existing:
                    label = Label(id=int(label_id), label=label_name)
                    self.db.add(label)
                    labels_imported += 1
        
        self.db.commit()
        return labels_imported
    
    def import_new_text_data(self, file_path: str) -> int:
        """
        Import new unlabeled text data from a file.
        
        Each line in the file is treated as a separate text record.
        
        Args:
            file_path: Path to the text file containing unlabeled data
            
        Returns:
            Number of new records imported
        """
        records_imported = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                text = line.strip()
                if text:  # Skip empty lines
                    # Check if text already exists
                    existing = self.db.query(AnnotationData).filter(AnnotationData.text == text).first()
                    if not existing:
                        annotation = AnnotationData(text=text, labels=None)
                        self.db.add(annotation)
                        records_imported += 1
        
        self.db.commit()
        return records_imported
    
    def get_all_unique_labels(self) -> Set[str]:
        """
        Get all unique labels from the annotation data.
        
        Returns:
            Set of all unique label names
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
        Sync labels table with unique labels found in annotation data.
        
        Returns:
            Number of new labels added
        """
        unique_labels = self.get_all_unique_labels()
        new_labels_count = 0
        
        # Get the max existing label ID
        max_id = self.db.query(Label).order_by(Label.id.desc()).first()
        next_id = (max_id.id + 1) if max_id else 0
        
        for label_name in unique_labels:
            existing = self.db.query(Label).filter(Label.label == label_name).first()
            if not existing:
                label = Label(id=next_id, label=label_name)
                self.db.add(label)
                next_id += 1
                new_labels_count += 1
        
        self.db.commit()
        return new_labels_count
    
    def __del__(self):
        """Clean up database session."""
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """Main function to run data import."""
    # Create tables if they don't exist
    create_tables()
    
    importer = DataImporter()
    
    # Import old data from the parent directory
    old_data_path = "../old-data"
    if os.path.exists(old_data_path):
        print("Importing old labeled data...")
        stats = importer.import_old_data(old_data_path)
        print(f"Import completed: {stats}")
        
        # Import label configuration
        config_path = os.path.join(old_data_path, "label_config.yaml")
        if os.path.exists(config_path):
            print("Importing label configuration...")
            labels_count = importer.import_label_config(config_path)
            print(f"Imported {labels_count} labels from config")
        
        # Sync any missing labels
        print("Syncing labels from annotation data...")
        new_labels = importer.sync_labels_from_annotations()
        print(f"Added {new_labels} new labels to labels table")
    else:
        print(f"Old data path {old_data_path} not found")


if __name__ == "__main__":
    main() 