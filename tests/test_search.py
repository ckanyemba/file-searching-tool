# ========================================
# 8. tests/test_search.py
# ========================================

"""
Test Search Functionality
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.similarity_engine import QuestionSimilarityEngine


class TestSearchEngine:
    
    def setup_method(self):
        self.engine = QuestionSimilarityEngine()
        
        # Sample questions
        self.questions = [
            {
                'question': 'Prove that PALINDROME is non-context-free.',
                'file': 'exam1.pdf',
                'location': {'page': 5}
            },
            {
                'question': 'Build a TM that accepts {a^n b^n}.',
                'file': 'exam2.pdf',
                'location': {'page': 3}
            },
            {
                'question': 'Show that PALINDROME is not a CFL.',
                'file': 'exam3.pdf',
                'location': {'page': 7}
            }
        ]
        
        self.engine.build_index(self.questions)
    
    def test_exact_match(self):
        """Test exact match search"""
        query = "Prove that PALINDROME is non-context-free."
        
        results = self.engine.find_exact_match(query)
        
        assert len(results) > 0
        assert results[0]['question'] == query
    
    def test_similar_match(self):
        """Test similar match search"""
        query = "Prove PALINDROME is not context-free"
        
        results = self.engine.search(query, top_k=3)
        
        assert len(results) > 0
        assert results[0]['combined_score'] > 0.5
    
    def test_top_k_results(self):
        """Test top-k limiting"""
        query = "PALINDROME"
        
        results = self.engine.search(query, top_k=2)
        
        assert len(results) <= 2
    
    def test_threshold_filtering(self):
        """Test threshold filtering"""
        query = "completely unrelated query"
        
        results = self.engine.search(query, threshold=0.8)
        
        # Should have few or no results
        assert len(results) == 0 or results[0]['combined_score'] >= 0.8

