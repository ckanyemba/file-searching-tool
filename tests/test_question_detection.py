
# ========================================
# 6. tests/test_question_detection.py
# ========================================

"""
Test Question Detection
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.question_detector import QuestionDetector
from src.utils.pattern_matcher import PatternMatcher


class TestQuestionDetector:
    
    def setup_method(self):
        self.detector = QuestionDetector()
    
    def test_detect_numbered_question(self):
        """Test detection of numbered questions"""
        text = "1. Prove that PALINDROME is non-context-free."
        
        questions = self.detector.detect_questions(text)
        
        assert len(questions) > 0
        assert "PALINDROME" in questions[0]['question']
    
    def test_detect_proof_question(self):
        """Test detection of proof questions"""
        text = "Prove that the language is regular."
        
        questions = self.detector.detect_questions(text)
        
        assert len(questions) > 0
        assert questions[0]['type'] in ['proof', 'show']
    
    def test_detect_build_question(self):
        """Test detection of build questions"""
        text = "Build a TM that accepts {a^n b^n}."
        
        questions = self.detector.detect_questions(text)
        
        assert len(questions) > 0
        assert questions[0]['type'] == 'build'
    
    def test_minimum_length_filter(self):
        """Test minimum length filtering"""
        text = "What?"
        
        questions = self.detector.detect_questions(text, min_length=10)
        
        assert len(questions) == 0
    
    def test_multiple_questions(self):
        """Test detection of multiple questions"""
        text = """
        1. Prove that PALINDROME is non-context-free.
        2. Build a TM that accepts {a^n b^n}.
        3. Find a CFG for the language.
        """
        
        questions = self.detector.detect_questions(text)
        
        assert len(questions) >= 3


class TestPatternMatcher:
    
    def setup_method(self):
        self.matcher = PatternMatcher()
    
    def test_extract_numbered_questions(self):
        """Test numbered question extraction"""
        text = "1. Question one\n2. Question two"
        
        questions = self.matcher.extract_numbered_questions(text)
        
        assert len(questions) == 2
        assert questions[0]['number'] == '1'
    
    def test_extract_roman_questions(self):
        """Test Roman numeral question extraction"""
        text = "(i) First question\n(ii) Second question"
        
        questions = self.matcher.extract_roman_questions(text)
        
        assert len(questions) == 2
        assert questions[0]['number'] == 'i'