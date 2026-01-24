"""
Complete Project Setup Script
Run this to set up the entire project structure
"""

import os
import sys
from pathlib import Path
import json

# Sample data content
SAMPLE_EXAM_TXT = """
UNIVERSITY OF SOUTH AFRICA
COS3701 - THEORETICAL COMPUTER SCIENCE III
EXAMINATION: OCTOBER/NOVEMBER 2025

QUESTION 1 [25 marks]

1. Prove that the language PALINDROME is non-context-free. [10 marks]

2. (i) Build a TM that accepts the language {a^n b^n}. [8 marks]
   (ii) Trace the execution of your TM on the input string "aabb". [7 marks]

QUESTION 2 [30 marks]

3. Consider the following grammar:
   S → aSb | ab
   
   (i) Show that this grammar generates {a^n b^n}. [10 marks]
   (ii) Convert this grammar to Chomsky Normal Form. [10 marks]
   (iii) Is this grammar ambiguous? Justify your answer. [10 marks]

QUESTION 3 [25 marks]

4. (i) Draw a PDA that accepts PALINDROME. [12 marks]
   (ii) Explain how your PDA works. [8 marks]
   (iii) Give an example trace. [5 marks]

QUESTION 4 [20 marks]

5. Find a regular expression for the language of all strings over {a,b} 
   that contain at least two a's. [10 marks]

6. Prove that the language {a^n b^n a^n} is not context-free using the 
   pumping lemma. [10 marks]

END OF EXAMINATION
"""

SAMPLE_QUESTIONS_JSON = [
    {
        "question": "Prove that the language PALINDROME is non-context-free.",
        "file": "sample_exam.txt",
        "type": "proof",
        "location": {"line": 8},
        "marks": 10
    },
    {
        "question": "Build a TM that accepts the language {a^n b^n}.",
        "file": "sample_exam.txt",
        "type": "build",
        "location": {"line": 10},
        "marks": 8
    },
    {
        "question": "Trace the execution of your TM on the input string 'aabb'.",
        "file": "sample_exam.txt",
        "type": "trace",
        "location": {"line": 11},
        "marks": 7
    }
]

TEST_QUERIES_TXT = """
# Test Queries for COS3701 Question Search

# Proof Questions
Prove that PALINDROME is non-context-free
Show that the language is regular
Demonstrate that the grammar is ambiguous

# Build Questions
Build a TM that accepts {a^n b^n}
Construct a PDA for PALINDROME
Design an FA for the language

# Find Questions
Find a CFG for the language
Determine if the string is in the language
Calculate the number of states needed

# Trace Questions
Trace the execution on input "aabb"
Follow the path through the automaton

# Convert Questions
Convert the NFA to an FA
Transform the grammar to CNF
"""


def create_directory_structure():
    """Create all necessary directories"""
    
    directories = [
        'database/exam_papers',
        'database/extracted_questions',
        'database/question_vectors',
        'src/core',
        'src/utils',
        'src/models',
        'src/api',
        'config',
        'scripts',
        'reports',
        'tests',
        'data_samples',
        'frontend',
        'logs',
    ]
    
    print("Creating directory structure...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print()


def create_init_files():
    """Create __init__.py files"""
    
    init_files = [
        'src/__init__.py',
        'src/core/__init__.py',
        'src/utils/__init__.py',
        'src/models/__init__.py',
        'src/api/__init__.py',
        'tests/__init__.py',
    ]
    
    print("Creating __init__.py files...")
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"  ✓ {init_file}")
    
    print()


def create_gitkeep_files():
    """Create .gitkeep files for empty directories"""
    
    gitkeep_dirs = [
        'database/exam_papers',
        'database/extracted_questions',
        'database/question_vectors',
        'logs',
        'reports',
    ]
    
    print("Creating .gitkeep files...")
    
    for directory in gitkeep_dirs:
        gitkeep_file = Path(directory) / '.gitkeep'
        gitkeep_file.touch()
        print(f"  ✓ {gitkeep_file}")
    
    print()


def create_sample_data():
    """Create sample data files"""
    
    print("Creating sample data files...")
    
    # Sample exam
    sample_exam = Path('data_samples/sample_exam.txt')
    sample_exam.write_text(SAMPLE_EXAM_TXT.strip())
    print(f"  ✓ {sample_exam}")
    
    # Sample questions
    sample_questions = Path('data_samples/sample_questions.json')
    sample_questions.write_text(json.dumps(SAMPLE_QUESTIONS_JSON, indent=2))
    print(f"  ✓ {sample_questions}")
    
    # Test queries
    test_queries = Path('data_samples/test_queries.txt')
    test_queries.write_text(TEST_QUERIES_TXT.strip())
    print(f"  ✓ {test_queries}")
    
    print()


def create_config_files():
    """Create configuration files"""
    
    print("Creating configuration files...")
    
    # .env.example
    env_example = Path('.env.example')
    env_content = """# Environment variables template
# Copy this to .env and fill in your values

# Application
DEBUG=false
LOG_LEVEL=INFO

# Paths
DATABASE_PATH=database
CACHE_DIR=.cache

# Model
MODEL_NAME=all-MiniLM-L6-v2
DEVICE=cpu

# Tesseract (Windows only, uncomment and set path)
# TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# API
API_HOST=0.0.0.0
API_PORT=8000
"""
    env_example.write_text(env_content)
    print(f"  ✓ {env_example}")
    
    # .gitignore
    gitignore = Path('.gitignore')
    if not gitignore.exists():
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
database/exam_papers/*
!database/exam_papers/.gitkeep
database/extracted_questions/*
!database/extracted_questions/.gitkeep
database/question_vectors/*
!database/question_vectors/.gitkeep
database/*.json

# Logs
logs/*.log
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env

# Models cache
.cache/
models/

# Test
.pytest_cache/
.coverage
htmlcov/
"""
        gitignore.write_text(gitignore_content)
        print(f"  ✓ {gitignore}")
    
    print()


def create_readme():
    """Create a basic README if it doesn't exist"""
    
    readme = Path('README.md')
    if readme.exists():
        print("README.md already exists, skipping...")
        return
    
    print("Creating README.md...")
    
    readme_content = """# COS3701 Question Search System

An intelligent question detection and search system for COS3701 exam papers.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place exam papers in database/exam_papers/**

3. **Build the index:**
   ```bash
   python main.py --rebuild
   ```

4. **Search:**
   ```bash
   python main.py --query "Prove that PALINDROME is non-context-free"
   ```

## Features

- Multi-format support (PDF, DOCX, PPTX, images)
- Semantic search using sentence transformers
- Question type classification
- Web interface
- REST API

## Project Structure

```
cos3701-question-search/
├── database/           # Question storage
├── src/               # Source code
├── frontend/          # Web interface
├── scripts/           # Utility scripts
└── tests/             # Test files
```

## Documentation

Run for help:
```bash
python main.py --help
```

## API Server

Start the API server:
```bash
python src/api/app.py
```

Then open: http://localhost:8000
"""
    readme.write_text(readme_content)
    print(f"  ✓ {readme}")
    print()


def print_next_steps():
    """Print next steps for the user"""
    
    print("\n" + "="*60)
    print("✓ Project setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Install Tesseract OCR (for image processing):")
    print("   - Ubuntu: sudo apt-get install tesseract-ocr")
    print("   - macOS: brew install tesseract")
    print("   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    print("\n3. Place your exam papers in: database/exam_papers/")
    print("\n4. Build the search index:")
    print("   python main.py --rebuild")
    print("\n5. Start searching!")
    print("   python main.py")
    print("\n" + "="*60)
    print()


def main():
    """Main setup function"""
    
    print("\n" + "="*60)
    print("COS3701 Question Search System - Setup")
    print("="*60)
    print()
    
    # Check if we're in the right directory
    if Path('setup_project.py').exists():
        print("⚠️  Warning: setup_project.py already exists.")
        print("   Are you running this from the project root?")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
        print()
    
    # Run setup steps
    try:
        create_directory_structure()
        create_init_files()
        create_gitkeep_files()
        create_sample_data()
        create_config_files()
        create_readme()
        
        # Print next steps
        print_next_steps()
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())