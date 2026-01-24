"""
COS3701 Question Search System
Main application entry point
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import argparse
import logging
from tqdm import tqdm

from src.utils.pdf_extractor import DocumentProcessor
from src.core.similarity_engine import QuestionSimilarityEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuestionSearchSystem:
    """Main question search system orchestrator"""
    
    def __init__(self, database_path: str = "database"):
        self.database_path = Path(database_path)
        self.exam_papers_dir = self.database_path / "exam_papers"
        self.extracted_dir = self.database_path / "extracted_questions"
        self.vectors_dir = self.database_path / "question_vectors"
        
        # Create directories if they don't exist
        for directory in [self.extracted_dir, self.vectors_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.processor = DocumentProcessor()
        self.search_engine = QuestionSimilarityEngine()
        
        self.all_questions = []
    
    def scan_exam_papers(self) -> List[Path]:
        """Scan for all supported exam papers"""
        supported_extensions = {'.pdf', '.docx', '.pptx', '.png', '.jpg', '.jpeg'}
        
        files = []
        if self.exam_papers_dir.exists():
            for ext in supported_extensions:
                files.extend(self.exam_papers_dir.glob(f'*{ext}'))
        
        logger.info(f"Found {len(files)} exam papers")
        return files
    
    def extract_all_questions(self, force_reextract: bool = False):
        """Extract questions from all exam papers"""
        files = self.scan_exam_papers()
        
        if not files:
            logger.warning(f"No exam papers found in {self.exam_papers_dir}")
            logger.info("Please add PDF/DOCX/PPTX files to database/exam_papers/")
            return
        
        for file_path in tqdm(files, desc="Extracting questions"):
            # Check if already extracted
            output_file = self.extracted_dir / f"{file_path.stem}_questions.json"
            
            if output_file.exists() and not force_reextract:
                logger.info(f"Loading cached questions from {output_file.name}")
                with open(output_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
            else:
                logger.info(f"Extracting questions from {file_path.name}")
                try:
                    questions = self.processor.extract_questions_from_document(str(file_path))
                    
                    # Save extracted questions
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(questions, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
                    questions = []
            
            self.all_questions.extend(questions)
        
        logger.info(f"Total questions extracted: {len(self.all_questions)}")
        
        # Save master list
        master_file = self.database_path / "questions_master.json"
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_questions, f, indent=2, ensure_ascii=False)
    
    def build_search_index(self):
        """Build the vector search index"""
        if not self.all_questions:
            logger.warning("No questions loaded. Run extract_all_questions() first.")
            return
        
        logger.info("Building search index...")
        self.search_engine.build_index(self.all_questions)
        
        # Save index
        index_file = self.vectors_dir / "faiss_index.bin"
        questions_file = self.vectors_dir / "questions_data.pkl"
        self.search_engine.save_index(str(index_file), str(questions_file))
    
    def load_search_index(self):
        """Load pre-built search index"""
        index_file = self.vectors_dir / "faiss_index.bin"
        questions_file = self.vectors_dir / "questions_data.pkl"
        
        if not index_file.exists() or not questions_file.exists():
            logger.error("Index files not found. Build index first.")
            return False
        
        logger.info("Loading search index...")
        self.search_engine.load_index(str(index_file), str(questions_file))
        self.all_questions = self.search_engine.questions
        return True
    
    def search_question(self, query: str, top_k: int = 5, 
                       search_type: str = 'semantic') -> List[Dict]:
        """Search for a question"""
        if search_type == 'exact':
            results = self.search_engine.find_exact_match(query)
            if results:
                return results
            logger.info("No exact match found, falling back to semantic search")
        
        if search_type == 'typed':
            results = self.search_engine.search_by_type(query, top_k=top_k)
        else:
            results = self.search_engine.search(query, top_k=top_k)
        
        return results
    
    def display_results(self, results: List[Dict]):
        """Display search results"""
        if not results:
            print("\nNo matching questions found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(results)} similar questions:")
        print(f"{'='*80}\n")
        
        for i, result in enumerate(results, 1):
            question_text = result['question']
            if len(question_text) > 150:
                question_text = question_text[:150] + "..."
            
            print(f"{i}. {question_text}")
            print(f"   File: {Path(result['file']).name}")
            
            if 'combined_score' in result:
                print(f"   Score: {result['combined_score']:.1%}")
            
            print(f"{'-'*80}\n")
    
    def generate_statistics(self) -> Dict:
        """Generate statistics"""
        if not self.all_questions:
            return {}
        
        stats = {
            'total_questions': len(self.all_questions),
            'questions_by_file': {},
            'questions_by_type': {},
        }
        
        for q in self.all_questions:
            filename = Path(q['file']).name
            stats['questions_by_file'][filename] = \
                stats['questions_by_file'].get(filename, 0) + 1
            
            if 'type' in q:
                q_type = q['type']
                stats['questions_by_type'][q_type] = \
                    stats['questions_by_type'].get(q_type, 0) + 1
        
        return stats
    
    def interactive_search(self):
        """Run interactive search session"""
        print("\n" + "="*80)
        print("COS3701 Question Search System")
        print("="*80)
        
        if not self.load_search_index():
            print("\nBuilding search index for the first time...")
            self.extract_all_questions()
            if not self.all_questions:
                print("\nError: No questions found. Add PDF files to database/exam_papers/")
                return
            self.build_search_index()
        
        stats = self.generate_statistics()
        print(f"\nDatabase: {stats['total_questions']} questions")
        print("\nCommands: search query, 'stats', or 'quit'")
        print("="*80 + "\n")
        
        while True:
            try:
                query = input("Enter question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if query.lower() == 'stats':
                    print(f"\nTotal: {stats['total_questions']}")
                    for f, c in stats['questions_by_file'].items():
                        print(f"  {f}: {c}")
                    continue
                
                results = self.search_question(query, top_k=5)
                self.display_results(results)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='COS3701 Question Search')
    parser.add_argument('--database', default='database', help='Database path')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild index')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results')
    
    args = parser.parse_args()
    
    system = QuestionSearchSystem(database_path=args.database)
    
    if args.rebuild:
        logger.info("Rebuilding database...")
        system.extract_all_questions(force_reextract=True)
        system.build_search_index()
        print("\n✓ Index rebuilt!")
        return
    
    if args.query:
        if not system.load_search_index():
            print("Index not found. Run: python main.py --rebuild")
            return
        results = system.search_question(args.query, top_k=args.top_k)
        system.display_results(results)
    else:
        system.interactive_search()


if __name__ == "__main__":
    main()
