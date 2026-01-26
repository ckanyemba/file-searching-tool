#!/usr/bin/env python3
"""
Diagnostic Check Script
Run this to identify why search isn't working
"""

import sys
from pathlib import Path
import json

print("\n" + "="*60)
print("COS3701 Question Search - Diagnostic Check")
print("="*60 + "\n")

# 1. Check Python version
print("1. Python Version:")
print(f"   {sys.version}")
if sys.version_info < (3, 8):
    print("   ⚠️  Python 3.8+ required")
else:
    print("   ✓ OK")

# 2. Check dependencies
print("\n2. Dependencies:")
required = {
    'PyMuPDF': 'fitz',
    'sentence-transformers': 'sentence_transformers',
    'faiss-cpu': 'faiss',
    'numpy': 'numpy',
    'flask': 'flask',
    'flask-cors': 'flask_cors'
}

missing = []
for name, module in required.items():
    try:
        __import__(module)
        print(f"   ✓ {name}")
    except ImportError:
        print(f"   ✗ {name} - MISSING")
        missing.append(name)

if missing:
    print(f"\n   Install missing: pip install {' '.join(missing)}")

# 3. Check database structure
print("\n3. Database Structure:")
db_path = Path('database')
if not db_path.exists():
    print("   ✗ database/ not found")
else:
    print("   ✓ database/ exists")
    
    # Check exam_papers
    exam_dir = db_path / 'exam_papers'
    if not exam_dir.exists():
        print("   ✗ database/exam_papers/ not found")
    else:
        pdfs = list(exam_dir.glob('*.pdf'))
        print(f"   ✓ database/exam_papers/ - {len(pdfs)} PDFs")
        for pdf in pdfs[:5]:  # Show first 5
            print(f"      - {pdf.name}")
        if len(pdfs) > 5:
            print(f"      ... and {len(pdfs)-5} more")

    # Check extracted questions
    extracted_dir = db_path / 'extracted_questions'
    if extracted_dir.exists():
        jsons = list(extracted_dir.glob('*.json'))
        print(f"   ✓ extracted_questions/ - {len(jsons)} files")
    else:
        print("   ⚠️  extracted_questions/ empty")

    # Check index
    index_file = db_path / 'question_vectors' / 'faiss_index.bin'
    questions_file = db_path / 'question_vectors' / 'questions_data.pkl'
    
    if index_file.exists():
        print(f"   ✓ Search index exists ({index_file.stat().st_size} bytes)")
    else:
        print("   ✗ Search index NOT BUILT")
    
    if questions_file.exists():
        print(f"   ✓ Questions data exists ({questions_file.stat().st_size} bytes)")
    else:
        print("   ✗ Questions data NOT BUILT")

# 4. Test PDF extraction
print("\n4. Testing PDF Extraction:")
try:
    import fitz
    exam_dir = Path('database/exam_papers')
    pdfs = list(exam_dir.glob('*.pdf'))
    
    if pdfs:
        test_pdf = pdfs[0]
        print(f"   Testing: {test_pdf.name}")
        
        doc = fitz.open(test_pdf)
        print(f"   ✓ Opened successfully - {len(doc)} pages")
        
        # Extract first page
        if len(doc) > 0:
            text = doc[0].get_text()
            print(f"   ✓ Page 1 text: {len(text)} characters")
            if len(text) < 100:
                print("   ⚠️  Very little text extracted - might be image-based PDF")
            print(f"\n   Preview:\n   {text[:200]}")
        
        doc.close()
    else:
        print("   ⚠️  No PDFs to test")
        
except ImportError:
    print("   ✗ PyMuPDF not installed - cannot test")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 5. Check if index has questions
print("\n5. Checking Index Contents:")
try:
    import pickle
    questions_file = Path('database/question_vectors/questions_data.pkl')
    
    if questions_file.exists():
        with open(questions_file, 'rb') as f:
            data = pickle.load(f)
            questions = data.get('questions', [])
            print(f"   ✓ Index contains {len(questions)} questions")
            
            if questions:
                print(f"\n   Sample question:")
                print(f"   {questions[0]['question'][:150]}...")
            else:
                print("   ⚠️  Index is empty!")
    else:
        print("   ✗ Index file not found")
        
except Exception as e:
    print(f"   ✗ Error reading index: {e}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if missing:
    print("\n❌ Install missing dependencies first:")
    print(f"   pip install {' '.join(missing)}")
elif not index_file.exists():
    print("\n⚠️  Search index not built. Run:")
    print("   python main.py --rebuild")
else:
    print("\n✓ System appears configured correctly")
    print("\nIf search still not working, check:")
    print("  1. API server running: python src/api/app.py")
    print("  2. Frontend pointing to correct URL")
    print("  3. Browser console for errors")

print("="*60 + "\n")