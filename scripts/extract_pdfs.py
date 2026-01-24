"""
========================
SCRIPTS AND TEST FILES
========================
"""

# ========================================
# 1. scripts/extract_pdfs.py
# ========================================

"""
Bulk PDF Extraction Script
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.pdf_extractor import DocumentProcessor
import json
from tqdm import tqdm
import argparse


def extract_all_pdfs(input_dir: str, output_dir: str):
    """Extract questions from all PDFs in a directory"""
    processor = DocumentProcessor()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all PDF files
    pdf_files = list(input_path.glob('*.pdf'))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    all_questions = []
    
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        print(f"\nProcessing: {pdf_file.name}")
        
        try:
            questions = processor.extract_questions_from_document(str(pdf_file))
            
            # Save individual file
            output_file = output_path / f"{pdf_file.stem}_questions.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            
            all_questions.extend(questions)
            print(f"  ✓ Extracted {len(questions)} questions")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save combined file
    combined_file = output_path / "all_questions.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Total questions extracted: {len(all_questions)}")
    print(f"✓ Saved to: {combined_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract questions from PDFs')
    parser.add_argument('input_dir', help='Directory containing PDF files')
    parser.add_argument('--output', '-o', default='extracted_questions',
                       help='Output directory')
    
    args = parser.parse_args()
    
    extract_all_pdfs(args.input_dir, args.output)