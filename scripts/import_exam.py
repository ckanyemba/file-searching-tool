# ========================================
# 2. scripts/import_exam.py
# ========================================

"""
Import Single Exam Paper
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.pdf_extractor import DocumentProcessor
from src.utils.date_parser import DateParser
import json
import argparse


def import_exam(file_path: str, output_dir: str):
    """Import a single exam paper"""
    processor = DocumentProcessor()
    date_parser = DateParser()
    
    file_path = Path(file_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Importing: {file_path.name}")
    
    # Extract questions
    questions = processor.extract_questions_from_document(str(file_path))
    
    # Parse date from filename
    date_info = date_parser.parse_filename(file_path.name)
    
    # Create metadata
    metadata = {
        'filename': file_path.name,
        'filepath': str(file_path),
        'date_info': date_info,
        'question_count': len(questions),
        'questions': questions
    }
    
    # Save
    output_file = output_path / f"{file_path.stem}_questions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Extracted {len(questions)} questions")
    print(f"✓ Saved to: {output_file}")
    
    if date_info:
        print(f"✓ Exam period: {date_info.get('period', 'Unknown')}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import single exam paper')
    parser.add_argument('file', help='Exam paper file (PDF, DOCX, etc.)')
    parser.add_argument('--output', '-o', default='database/extracted_questions',
                       help='Output directory')
    
    args = parser.parse_args()
    
    import_exam(args.file, args.output)

