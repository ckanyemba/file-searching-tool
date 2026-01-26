#!/usr/bin/env python3
"""
Simplified COS3701 Question Search
Minimal version that WORKS
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try imports with fallbacks
try:
    import fitz  # PyMuPDF
except ImportError:
    logger.error("PyMuPDF not installed: pip install PyMuPDF")
    fitz = None

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    logger.warning("sentence-transformers not installed - using basic search only")
    SentenceTransformer = None
    np = None

try:
    import faiss
except ImportError:
    logger.warning("faiss not installed - using basic search only")
    faiss = None


class SimpleQuestionSearcher:
    """Simplified question search system"""
    
    def __init__(self, db_path="database"):
        self.db_path = Path(db_path)
        self.exam_papers_dir = self.db_path / "exam_papers"
        self.extracted_dir = self.db_path / "extracted_questions"
        self.vectors_dir = self.db_path / "question_vectors"
        
        # Create dirs
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        self.vectors_dir.mkdir(parents=True, exist_ok=True)
        
        self.questions = []
        self.embeddings = None
        self.index = None
        self.model = None
        
        # Load model if available - FORCE CPU
        if SentenceTransformer:
            try:
                # Force CPU usage to avoid CUDA errors
                self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                logger.info("✓ Loaded sentence transformer model (CPU mode)")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from PDF"""
        if not fitz:
            return ""
        
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting {pdf_path}: {e}")
            return ""
    
    def detect_questions(self, text: str) -> List[str]:
        """Simple question detection"""
        # Split by common question patterns
        patterns = [
            # Numbered questions: "1.", "2.", etc.
            r'(\d+)\.\s+([^.?!]+[.?!])',
            # Questions with keywords
            r'((?:Prove|Show|Build|Find|Draw|Construct|Explain|Describe|Trace)[^.?!]+[.?!])',
        ]
        
        questions = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                q = match.group(0).strip()
                # Filter by length
                if 20 < len(q) < 500:
                    questions.append(q)
        
        # Also split by newlines and check each line
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # If line looks like a question
            if line and (
                line.endswith('?') or
                any(keyword in line.lower() for keyword in 
                    ['prove', 'show', 'build', 'find', 'draw', 'construct'])
            ):
                if 20 < len(line) < 500:
                    questions.append(line)
        
        # Deduplicate
        return list(set(questions))
    
    def extract_from_all_pdfs(self, force=False):
        """Extract questions from all PDFs"""
        if not self.exam_papers_dir.exists():
            logger.error(f"Directory not found: {self.exam_papers_dir}")
            return
        
        pdfs = list(self.exam_papers_dir.glob('*.pdf'))
        logger.info(f"Found {len(pdfs)} PDF files")
        
        all_questions = []
        
        for pdf_path in pdfs:
            logger.info(f"Processing: {pdf_path.name}")
            
            # Check cache
            cache_file = self.extracted_dir / f"{pdf_path.stem}_questions.json"
            
            if cache_file.exists() and not force:
                logger.info(f"  Loading from cache")
                with open(cache_file) as f:
                    questions = json.load(f)
            else:
                # Extract text
                logger.info(f"  Extracting text...")
                text = self.extract_text_from_pdf(str(pdf_path))
                
                if not text:
                    logger.warning(f"  No text extracted")
                    continue
                
                logger.info(f"  Extracted {len(text)} characters")
                
                # Detect questions
                logger.info(f"  Detecting questions...")
                question_texts = self.detect_questions(text)
                logger.info(f"  Found {len(question_texts)} questions")
                
                # Format
                questions = [
                    {
                        'question': q,
                        'file': str(pdf_path),
                        'source': pdf_path.name
                    }
                    for q in question_texts
                ]
                
                # Cache
                with open(cache_file, 'w') as f:
                    json.dump(questions, f, indent=2)
            
            all_questions.extend(questions)
        
        self.questions = all_questions
        logger.info(f"Total questions: {len(self.questions)}")
        
        # Save master list
        master_file = self.db_path / "questions_master.json"
        with open(master_file, 'w') as f:
            json.dump(self.questions, f, indent=2)
    
    def build_index(self):
        """Build search index"""
        if not self.questions:
            logger.error("No questions loaded")
            return
        
        if not self.model:
            logger.warning("No model - skipping vector index")
            return
        
        logger.info("Computing embeddings...")
        texts = [q['question'] for q in self.questions]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        if faiss:
            logger.info("Building FAISS index...")
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))
            
            # Save
            index_file = self.vectors_dir / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            logger.info(f"Saved index to {index_file}")
        
        # Save questions and embeddings
        import pickle
        data_file = self.vectors_dir / "questions_data.pkl"
        with open(data_file, 'wb') as f:
            pickle.dump({
                'questions': self.questions,
                'embeddings': self.embeddings
            }, f)
        logger.info(f"Saved data to {data_file}")
    
    def load_index(self):
        """Load existing index"""
        index_file = self.vectors_dir / "faiss_index.bin"
        data_file = self.vectors_dir / "questions_data.pkl"
        
        if not data_file.exists():
            logger.warning("Index not found")
            return False
        
        # Load data
        import pickle
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
            self.questions = data['questions']
            self.embeddings = data.get('embeddings')
        
        # Load FAISS index
        if faiss and index_file.exists():
            self.index = faiss.read_index(str(index_file))
        
        logger.info(f"Loaded {len(self.questions)} questions")
        return True
    
    def search_basic(self, query: str, top_k=5) -> List[Dict]:
        """Basic keyword search (no ML)"""
        query_lower = query.lower()
        results = []
        
        for q in self.questions:
            text_lower = q['question'].lower()
            
            # Count matching words
            query_words = set(query_lower.split())
            text_words = set(text_lower.split())
            matches = len(query_words & text_words)
            
            if matches > 0:
                score = matches / len(query_words) if query_words else 0
                results.append({
                    **q,
                    'score': score,
                    'matches': matches
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def search_semantic(self, query: str, top_k=5) -> List[Dict]:
        """Semantic search using embeddings"""
        if not self.model or not self.index:
            logger.warning("Model/index not available - using basic search")
            return self.search_basic(query, top_k)
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Search
        k = min(top_k * 2, len(self.questions))
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), k
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.questions):
                results.append({
                    **self.questions[idx],
                    'score': float(1 / (1 + dist)),
                    'distance': float(dist)
                })
        
        return results[:top_k]
    
    def search(self, query: str, top_k=5) -> List[Dict]:
        """Main search function"""
        if self.model and self.index:
            return self.search_semantic(query, top_k)
        else:
            return self.search_basic(query, top_k)


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Question Search')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild index')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results')
    
    args = parser.parse_args()
    
    searcher = SimpleQuestionSearcher()
    
    if args.rebuild:
        print("\nRebuilding index...")
        searcher.extract_from_all_pdfs(force=True)
        searcher.build_index()
        print("\n✓ Index rebuilt!\n")
        return
    
    if args.query:
        # Load index
        if not searcher.load_index():
            print("Index not found. Run: python simple_main.py --rebuild")
            return
        
        # Search
        print(f"\nSearching for: {args.query}\n")
        results = searcher.search(args.query, top_k=args.top_k)
        
        if not results:
            print("No results found.\n")
        else:
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['question'][:100]}...")
                print(f"   File: {r['source']}")
                print(f"   Score: {r['score']:.2%}\n")
    else:
        # Interactive
        if not searcher.load_index():
            print("Index not found. Run: python simple_main.py --rebuild")
            return
        
        print("\n" + "="*60)
        print(f"Loaded {len(searcher.questions)} questions")
        print("Type 'quit' to exit\n")
        
        while True:
            query = input("Search: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            results = searcher.search(query, top_k=5)
            print()
            
            if not results:
                print("No results found.\n")
            else:
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r['question'][:100]}...")
                    print(f"   File: {r['source']}")
                    print(f"   Score: {r['score']:.2%}\n")


if __name__ == '__main__':
    main()