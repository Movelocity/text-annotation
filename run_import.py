#!/usr/bin/env python3
"""
Script to import old data and initialize the text annotation database.

This script:
1. Creates database tables
2. Imports old labeled data from directory structure
3. Imports label configuration
4. Displays import statistics
"""

import os
import sys
from data_import import DataImporter, main as import_main


def run_full_import():
    """Run the complete data import process."""
    print("="*60)
    print("Text Annotation System - Data Import")
    print("="*60)
    
    # Run the main import function
    import_main()
    
    print("="*60)
    print("Import process completed!")
    print("="*60)
    
    # Display some basic statistics
    try:
        from models import SessionLocal
        from services import StatisticsService
        
        db = SessionLocal()
        stats_service = StatisticsService(db)
        stats = stats_service.get_system_stats()
        
        print("\nCurrent Database Statistics:")
        print(f"- Total texts: {stats.total_texts}")
        print(f"- Labeled texts: {stats.labeled_texts}")
        print(f"- Unlabeled texts: {stats.unlabeled_texts}")
        print(f"- Total unique labels: {stats.total_labels}")
        
        if stats.label_stats:
            print(f"\nTop 10 most common labels:")
            for i, label_stat in enumerate(stats.label_stats[:10], 1):
                print(f"  {i:2d}. {label_stat.label}: {label_stat.count} texts")
        
        db.close()
        
    except Exception as e:
        print(f"Error getting statistics: {e}")


if __name__ == "__main__":
    run_full_import() 