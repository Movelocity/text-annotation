#!/usr/bin/env python3
"""
Demo script for the text annotation system.

This script demonstrates:
1. Searching for annotations
2. Creating new annotations
3. Bulk labeling
4. Getting statistics
"""

import requests
import json
from typing import List, Dict

# API base URL
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def search_annotations(query: str = None, labels: str = None, unlabeled_only: bool = False, 
                      page: int = 1, per_page: int = 5) -> Dict:
    """Search for annotations with various filters."""
    payload = {
        "page": page,
        "per_page": per_page,
        "unlabeled_only": unlabeled_only
    }
    
    if query:
        payload["query"] = query
    if labels:
        payload["labels"] = labels
        
    response = requests.post(f"{BASE_URL}/annotations/search", json=payload)
    return response.json()


def create_annotation(text: str, labels: str = None) -> Dict:
    """Create a new annotation."""
    payload = {"text": text}
    if labels:
        payload["labels"] = labels
        
    response = requests.post(f"{BASE_URL}/annotations/", json=payload)
    return response.json()


def import_texts(texts: List[str]) -> Dict:
    """Import multiple texts as unlabeled data."""
    payload = {"texts": texts}
    response = requests.post(f"{BASE_URL}/annotations/import-texts", json=payload)
    return response.json()


def bulk_label(text_ids: List[int], labels: str) -> Dict:
    """Apply labels to multiple texts."""
    payload = {"text_ids": text_ids, "labels": labels}
    response = requests.post(f"{BASE_URL}/annotations/bulk-label", json=payload)
    return response.json()


def get_system_stats() -> Dict:
    """Get system statistics."""
    response = requests.get(f"{BASE_URL}/stats/system")
    return response.json()


def get_all_labels() -> List[Dict]:
    """Get all labels."""
    response = requests.get(f"{BASE_URL}/labels/")
    return response.json()


def demo_search_operations():
    """Demonstrate search operations."""
    print_section("SEARCH OPERATIONS")
    
    # Search by text content
    print("1. Searching for texts containing 'refund':")
    results = search_annotations(query="refund", per_page=3)
    print(f"Found {results['total']} texts")
    for item in results['items']:
        print(f"  ID: {item['id']}, Labels: {item['labels']}")
        print(f"  Text: {item['text'][:100]}...")
    
    # Search by label
    print("\n2. Searching for texts with 'angry' label:")
    results = search_annotations(labels="angry", per_page=3)
    print(f"Found {results['total']} texts with 'angry' label")
    for item in results['items']:
        print(f"  ID: {item['id']}, Text: {item['text'][:80]}...")
    
    # Search for unlabeled texts (there shouldn't be any after import)
    print("\n3. Searching for unlabeled texts:")
    results = search_annotations(unlabeled_only=True, per_page=5)
    print(f"Found {results['total']} unlabeled texts")


def demo_create_and_label():
    """Demonstrate creating new annotations and labeling."""
    print_section("CREATE AND LABEL OPERATIONS")
    
    # Import some new unlabeled texts
    new_texts = [
        "Hello, I need help with my order",
        "When will my package arrive?",
        "I want to return this product",
        "The item is damaged, please send replacement",
        "Thank you for the fast shipping!"
    ]
    
    print("1. Importing new unlabeled texts:")
    result = import_texts(new_texts)
    print(f"Imported {result['imported_count']} new texts")
    
    # Search for unlabeled texts
    print("\n2. Finding newly imported unlabeled texts:")
    results = search_annotations(unlabeled_only=True, per_page=10)
    print(f"Found {results['total']} unlabeled texts")
    
    if results['items']:
        # Get IDs of the first few unlabeled texts
        text_ids = [item['id'] for item in results['items'][:3]]
        
        print(f"\n3. Bulk labeling texts with IDs: {text_ids}")
        bulk_result = bulk_label(text_ids, "customer_service,inquiry")
        print(f"Updated {bulk_result['updated_count']} texts")
        
        # Verify the labeling
        print("\n4. Verifying the labels were applied:")
        for text_id in text_ids:
            response = requests.get(f"{BASE_URL}/annotations/{text_id}")
            if response.status_code == 200:
                item = response.json()
                print(f"  ID: {item['id']}, Labels: {item['labels']}")
                print(f"  Text: {item['text'][:60]}...")


def demo_statistics():
    """Demonstrate statistics operations."""
    print_section("STATISTICS")
    
    stats = get_system_stats()
    print(f"Total texts: {stats['total_texts']:,}")
    print(f"Labeled texts: {stats['labeled_texts']:,}")
    print(f"Unlabeled texts: {stats['unlabeled_texts']:,}")
    print(f"Total unique labels: {stats['total_labels']}")
    
    print(f"\nTop 10 most common labels:")
    for i, label_stat in enumerate(stats['label_stats'][:10], 1):
        print(f"  {i:2d}. {label_stat['label']}: {label_stat['count']:,} texts")


def demo_label_management():
    """Demonstrate label management."""
    print_section("LABEL MANAGEMENT")
    
    labels = get_all_labels()
    print(f"Total labels in system: {len(labels)}")
    
    print("\nSample labels:")
    for label in labels[:10]:
        print(f"  ID: {label['id']:3d}, Label: {label['label']}")


def main():
    """Main demo function."""
    print("Text Annotation System - API Demo")
    print("Make sure the server is running at http://localhost:8000")
    
    try:
        # Test server connectivity
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("ERROR: Server is not responding!")
            return
        
        print("✓ Server is running")
        
        # Run demonstrations
        demo_statistics()
        demo_label_management()
        demo_search_operations()
        demo_create_and_label()
        
        # Final statistics
        demo_statistics()
        
        print_section("DEMO COMPLETED")
        print("API Demo completed successfully!")
        print("You can explore more endpoints at: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to the server!")
        print("Make sure the server is running: uv run python main.py")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main() 