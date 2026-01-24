# ========================================
# 3. scripts/rebuild_index.py
# ========================================

"""
Rebuild Search Index
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main import QuestionSearchSystem
import argparse


def rebuild_index(database_path: str, force: bool = False):
    """Rebuild the search index"""
    print("Rebuilding search index...")
    
    system = QuestionSearchSystem(database_path=database_path)
    
    # Extract questions
    print("\n1. Extracting questions from exam papers...")
    system.extract_all_questions(force_reextract=force)
    print(f"   ✓ Extracted {len(system.all_questions)} questions")
    
    # Build index
    print("\n2. Building search index...")
    system.build_search_index()
    print("   ✓ Index built successfully")
    
    # Show statistics
    stats = system.generate_statistics()
    
    print("\n" + "="*50)
    print("Statistics:")
    print("="*50)
    print(f"Total questions: {stats['total_questions']}")
    print(f"\nQuestions by file:")
    for filename, count in stats['questions_by_file'].items():
        print(f"  - {filename}: {count}")
    
    print("\n✓ Index rebuild complete!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rebuild search index')
    parser.add_argument('--database', default='database',
                       help='Database directory path')
    parser.add_argument('--force', action='store_true',
                       help='Force re-extraction of questions')
    
    args = parser.parse_args()
    
    rebuild_index(args.database, args.force)