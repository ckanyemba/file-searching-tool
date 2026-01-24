# ========================================
# 5. scripts/export_data.py
# ========================================

"""
Export Data Script
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main import QuestionSearchSystem
import json
import csv
import argparse


def export_to_json(questions: list, output_file: str):
    """Export to JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)


def export_to_csv(questions: list, output_file: str):
    """Export to CSV"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['question', 'file', 'type', 'location']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for q in questions:
            writer.writerow({
                'question': q['question'],
                'file': q['file'],
                'type': q.get('type', 'unknown'),
                'location': str(q.get('location', ''))
            })


def export_to_txt(questions: list, output_file: str):
    """Export to plain text"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, q in enumerate(questions, 1):
            f.write(f"{i}. {q['question']}\n")
            f.write(f"   File: {q['file']}\n")
            f.write(f"   Type: {q.get('type', 'unknown')}\n")
            f.write("\n")


def export_data(database_path: str, output_file: str, format: str):
    """Export data in specified format"""
    system = QuestionSearchSystem(database_path=database_path)
    
    if not system.load_search_index():
        print("Error: Index not found. Run rebuild_index.py first.")
        return
    
    questions = system.all_questions
    
    exporters = {
        'json': export_to_json,
        'csv': export_to_csv,
        'txt': export_to_txt
    }
    
    exporter = exporters.get(format)
    if not exporter:
        print(f"Error: Unsupported format '{format}'")
        return
    
    exporter(questions, output_file)
    
    print(f"✓ Exported {len(questions)} questions to {output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export question data')
    parser.add_argument('output_file', help='Output file path')
    parser.add_argument('--database', default='database',
                       help='Database directory path')
    parser.add_argument('--format', '-f', 
                       choices=['json', 'csv', 'txt'],
                       default='json',
                       help='Export format')
    
    args = parser.parse_args()
    
    export_data(args.database, args.output_file, args.format)
