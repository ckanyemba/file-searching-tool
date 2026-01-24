"""
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
                # Force CPU usage
                self.model = SentenceTransformer(model_name, device='cpu')
                logger.info(f"Loaded model on CPU: {model_name}")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
                self.model = None
    
    def preprocess_question(self, question: str) -> str:
        """Clean question text"""
        text = re.sub(r'\s+', ' ', question).strip()
        text = re.sub(r'^\d+[\.)]\s*', '', text)
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
        
        logger.info(f"Computing embeddings for {len(question_texts)} questions...")
        self.embeddings = self.compute_embeddings(question_texts)
        
        if HAS_FAISS:
            dimension = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(self.embeddings.astype('float32'))
            logger.info("FAISS index built")
    
    def save_index(self, index_path: str, questions_path: str):
        """Save index"""
        if HAS_FAISS and self.faiss_index:
            faiss.write_index(self.faiss_index, index_path)
        with open(questions_path, 'wb') as f:
            pickle.dump({'questions': self.questions, 'embeddings': self.embeddings}, f)
        logger.info(f"Index saved to {index_path}")
    
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
        logger.info(f"Index loaded")
    
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
        if re.search(r'\b(prove|show|demonstrate)\b', q_lower):
            return 'proof'
        if re.search(r'\b(build|construct|design|draw)\b', q_lower):
            return 'build'
        if re.search(r'\b(find|determine|calculate)\b', q_lower):
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
