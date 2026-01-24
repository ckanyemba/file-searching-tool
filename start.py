"""
Quick Start Script
Sets up and runs the application
"""

import subprocess
import sys
from pathlib import Path


def check_requirements():
    """Check if requirements are installed"""
    
    print("Checking requirements...")
    
    required_packages = [
        'sentence-transformers',
        'PyMuPDF',
        'python-docx',
        'python-pptx',
        'Pillow',
        'pytesseract',
        'faiss-cpu',
        'scikit-learn',
        'numpy',
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("✓ All requirements installed")
    return True


def check_database():
    """Check if database is set up"""
    
    print("\nChecking database...")
    
    db_path = Path('database')
    if not db_path.exists():
        print("⚠️  Database directory not found")
        return False
    
    exam_papers = list(Path('database/exam_papers').glob('*.pdf'))
    
    if not exam_papers:
        print("⚠️  No exam papers found in database/exam_papers/")
        print("   Place your PDF files there first")
        return False
    
    print(f"✓ Found {len(exam_papers)} exam papers")
    return True


def build_index():
    """Build search index"""
    
    print("\nBuilding search index...")
    
    cmd = [sys.executable, 'main.py', '--rebuild']
    result = subprocess.run(cmd)
    
    return result.returncode == 0


def start_interactive():
    """Start interactive search"""
    
    print("\nStarting interactive search...")
    
    cmd = [sys.executable, 'main.py']
    subprocess.run(cmd)


def main():
    """Main quick start function"""
    
    print("\n" + "="*60)
    print("COS3701 Question Search - Quick Start")
    print("="*60)
    print()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Check if index exists
    index_file = Path('database/question_vectors/faiss_index.bin')
    
    if not index_file.exists():
        print("\n⚠️  Search index not found")
        response = input("   Build index now? (y/n): ")
        
        if response.lower() == 'y':
            if not build_index():
                print("\n✗ Index build failed")
                sys.exit(1)
        else:
            print("\nRun this to build index:")
            print("  python main.py --rebuild")
            sys.exit(0)
    
    # Start interactive search
    start_interactive()


if __name__ == '__main__':
    main()


# ========================================
# 7. LICENSE
# ========================================

LICENSE_MIT = """
MIT License

Copyright (c) 2024 COS3701 Question Search

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


# ========================================
# Save these files helper
# ========================================

def save_all_sample_files():
    """Helper function to save all sample files"""
    
    files = {
        'data_samples/sample_exam.txt': SAMPLE_EXAM_TXT.strip(),
        'data_samples/sample_questions.json': SAMPLE_QUESTIONS_JSON.strip(),
        'data_samples/test_queries.txt': TEST_QUERIES_TXT.strip(),
        'LICENSE': LICENSE_MIT.strip(),
    }
    
    for filepath, content in files.items():
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        print(f"✓ Created {filepath}")


if __name__ == '__main__':
    # If running this file directly, save all sample files
    save_all_sample_files()