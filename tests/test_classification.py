
# ========================================
# 7. tests/test_classification.py
# ========================================

"""
Test Question Classification
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.question_classifier import QuestionClassifier, QuestionType


class TestQuestionClassifier:
    
    def setup_method(self):
        self.classifier = QuestionClassifier()
    
    def test_classify_proof_question(self):
        """Test proof question classification"""
        question = "Prove that PALINDROME is non-context-free."
        
        q_type = self.classifier.classify(question)
        
        assert q_type == QuestionType.PROOF
    
    def test_classify_build_question(self):
        """Test build question classification"""
        question = "Build a TM that accepts the language."
        
        q_type = self.classifier.classify(question)
        
        assert q_type == QuestionType.BUILD
    
    def test_classify_find_question(self):
        """Test find question classification"""
        question = "Find a CFG for the language."
        
        q_type = self.classifier.classify(question)
        
        assert q_type == QuestionType.FIND
    
    def test_get_question_metadata(self):
        """Test metadata extraction"""
        question = "Prove that PALINDROME is non-context-free?"
        
        metadata = self.classifier.get_question_metadata(question)
        
        assert 'type' in metadata
        assert 'length' in metadata
        assert 'has_question_mark' in metadata
        assert metadata['has_question_mark'] == True
