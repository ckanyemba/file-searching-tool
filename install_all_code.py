#!/usr/bin/env python3
"""
Complete Code Installer
Run this to install ALL the code automatically
"""

from pathlib import Path

print("\n" + "="*60)
print("Installing COS3701 Question Search System Code")
print("="*60 + "\n")

# Define all files and their content
files_to_create = {
    
# ============================================================
# src/utils/pdf_extractor.py
# ============================================================
'src/utils/pdf_extractor.py': '''"""
Document Processing Module
Extracts text from PDF, DOCX, PPTX, and images
"""

import re
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from pptx import Presentation
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class DocumentProcessor:
    """Extract text and questions from various document formats"""
    
    def __init__(self):
        self.question_patterns = [
            r'\\b\\d+\\.\\s+.*?\\?',
            r'\\([ivxlcdm]+\\)\\s+.*?[.?]',
            r'Question\\s+\\d+:.*?[.?]',
            r'Problem\\s+\\d+:.*?[.?]',
            r'^[A-Z].*?\\?$',
            r'\\bProve that.*?[.]',
            r'\\bShow that.*?[.]',
            r'\\bBuild.*?[.]',
            r'\\bDraw.*?[.]',
            r'\\bFind.*?[.]',
        ]
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Extract text from PDF"""
        if not HAS_PYMUPDF:
            return None
        
        text_content = []
        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    text_content.append({
                        'page': page_num + 1,
                        'text': text,
                        'source': 'direct'
                    })
            doc.close()
            return {
                'file_path': file_path,
                'file_type': 'pdf',
                'text_content': text_content,
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    def process_file(self, file_path: str) -> Dict:
        """Process file based on extension"""
        path = Path(file_path)
        if path.suffix.lower() == '.pdf':
            return self.extract_from_pdf(str(path))
        return None
    
    def detect_questions(self, text: str) -> List[str]:
        """Detect questions in text"""
        questions = []
        for pattern in self.question_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                question = match.group(0).strip()
                if len(question) > 10:
                    questions.append(question)
        return list(set(questions))
    
    def extract_questions_from_document(self, file_path: str) -> List[Dict]:
        """Extract all questions from a document"""
        doc_data = self.process_file(file_path)
        if not doc_data:
            return []
        
        all_questions = []
        for content in doc_data.get('text_content', []):
            text = content.get('text', '')
            questions = self.detect_questions(text)
            
            for q in questions:
                all_questions.append({
                    'question': q,
                    'file': file_path,
                    'location': content,
                    'type': 'text'
                })
        
        return all_questions
''',

# ============================================================
# src/core/similarity_engine.py
# ============================================================
'src/core/similarity_engine.py': '''"""
Question Similarity Engine
"""

import numpy as np
from typing import List, Dict
import re
from difflib import SequenceMatcher
import logging
import pickle

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


class QuestionSimilarityEngine:
    """Find similar questions"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = None
        self.questions = []
        self.embeddings = None
        self.faiss_index = None
        
        if HAS_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(model_name)
            except:
                self.model = None
    
    def preprocess_question(self, question: str) -> str:
        """Clean question text"""
        text = re.sub(r'\\s+', ' ', question).strip()
        text = re.sub(r'^\\d+[\\.)\\s]*', '', text)
        return text
    
    def compute_embeddings(self, questions: List[str]) -> np.ndarray:
        """Compute embeddings"""
        if not self.model:
            return np.random.rand(len(questions), 384).astype('float32')
        preprocessed = [self.preprocess_question(q) for q in questions]
        return self.model.encode(preprocessed, show_progress_bar=True)
    
    def build_index(self, questions: List[Dict]):
        """Build search index"""
        self.questions = questions
        question_texts = [q['question'] for q in questions]
        
        self.embeddings = self.compute_embeddings(question_texts)
        
        if HAS_FAISS:
            dimension = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(self.embeddings.astype('float32'))
    
    def save_index(self, index_path: str, questions_path: str):
        """Save index"""
        if HAS_FAISS and self.faiss_index:
            faiss.write_index(self.faiss_index, index_path)
        with open(questions_path, 'wb') as f:
            pickle.dump({'questions': self.questions, 'embeddings': self.embeddings}, f)
    
    def load_index(self, index_path: str, questions_path: str):
        """Load index"""
        if HAS_FAISS:
            try:
                self.faiss_index = faiss.read_index(index_path)
            except:
                pass
        with open(questions_path, 'rb') as f:
            data = pickle.load(f)
            self.questions = data['questions']
            self.embeddings = data['embeddings']
    
    def string_similarity(self, s1: str, s2: str) -> float:
        """String similarity"""
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict]:
        """Search for similar questions"""
        if not self.questions:
            return []
        
        query_embedding = self.compute_embeddings([query])[0]
        
        if HAS_FAISS and self.faiss_index:
            k = min(top_k * 2, len(self.questions))
            distances, indices = self.faiss_index.search(
                query_embedding.reshape(1, -1).astype('float32'), k)
            
            max_distance = np.max(distances[0]) if len(distances[0]) > 0 else 1.0
            similarities = 1 - (distances[0] / (max_distance + 1e-6))
            
            results = []
            for idx, sim in zip(indices[0], similarities):
                if idx < len(self.questions):
                    q = self.questions[idx]
                    string_sim = self.string_similarity(query, q['question'])
                    combined = 0.7 * sim + 0.3 * string_sim
                    
                    if combined >= threshold:
                        results.append({
                            'question': q['question'],
                            'file': q['file'],
                            'location': q.get('location', {}),
                            'semantic_score': float(sim),
                            'string_score': float(string_sim),
                            'combined_score': float(combined),
                            'metadata': q
                        })
        else:
            results = []
            for q in self.questions:
                sim = self.string_similarity(query, q['question'])
                if sim >= threshold:
                    results.append({
                        'question': q['question'],
                        'file': q['file'],
                        'location': q.get('location', {}),
                        'combined_score': float(sim),
                        'metadata': q
                    })
        
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        return results[:top_k]
    
    def find_exact_match(self, query: str) -> List[Dict]:
        """Find exact matches"""
        query_clean = self.preprocess_question(query).lower()
        matches = []
        for q in self.questions:
            if self.preprocess_question(q['question']).lower() == query_clean:
                matches.append({**q, 'match_type': 'exact'})
        return matches
    
    def classify_question_type(self, question: str) -> str:
        """Classify question type"""
        q_lower = question.lower()
        if re.search(r'\\b(prove|show|demonstrate)\\b', q_lower):
            return 'proof'
        if re.search(r'\\b(build|construct|design|draw)\\b', q_lower):
            return 'build'
        if re.search(r'\\b(find|determine|calculate)\\b', q_lower):
            return 'find'
        return 'general'
    
    def search_by_type(self, query: str, question_type: str = None, top_k: int = 5) -> List[Dict]:
        """Search by type"""
        all_results = self.search(query, top_k=top_k * 2)
        if question_type is None:
            question_type = self.classify_question_type(query)
        
        filtered = []
        for r in all_results:
            if self.classify_question_type(r['question']) == question_type:
                r['question_type'] = question_type
                filtered.append(r)
        return filtered[:top_k]
''',

# ============================================================
# src/utils/text_cleaner.py
# ============================================================
'src/utils/text_cleaner.py': '''"""
Text cleaning utilities
"""

import re
import unicodedata


class TextCleaner:
    """Clean and normalize text"""
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        return re.sub(r'\\s+', ' ', text).strip()
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        return unicodedata.normalize('NFKD', text)
    
    @staticmethod
    def clean(text: str, full_clean: bool = False) -> str:
        text = TextCleaner.normalize_unicode(text)
        text = TextCleaner.remove_extra_whitespace(text)
        return text
''',

# ============================================================
# src/api/endpoints.py
# ============================================================
'src/api/endpoints.py': '''"""
API Endpoints
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')
search_system = None


def init_endpoints(system):
    """Initialize endpoints"""
    global search_system
    search_system = system


@api_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search endpoint"""
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
    else:
        query = request.args.get('query', '')
        top_k = int(request.args.get('top_k', 5))
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        if search_system:
            results = search_system.search_question(query=query, top_k=top_k)
        else:
            results = []
        return jsonify({'query': query, 'results': results, 'total': len(results)})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
def stats():
    """Stats endpoint"""
    try:
        if search_system:
            data = search_system.generate_statistics()
        else:
            data = {'total_questions': 0}
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})
''',

}

# Create all files
print("Creating files...\n")
created_count = 0

for filepath, content in files_to_create.items():
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"✓ {filepath}")
    created_count += 1

print(f"\n{'='*60}")
print(f"✓ Created {created_count} files successfully!")
print(f"{'='*60}")
print("\nYou can now run:")
print("  python3 main.py --rebuild")
print("  python3 src/api/app.py")
print(f"{'='*60}\n")