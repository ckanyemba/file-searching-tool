"""
========================
REMAINING CODE FILES
========================
"""

# ========================================
# 1. src/core/question_detector.py
# ========================================

"""
Question Detection Module
Combines multiple detection strategies
"""

import re
from typing import List, Dict, Optional
from pathlib import Path
import logging

from ..utils.pattern_matcher import PatternMatcher
from .question_classifier import QuestionClassifier

logger = logging.getLogger(__name__)


class QuestionDetector:
    """Detect and extract questions from text"""
    
    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self.classifier = QuestionClassifier()
        
        # Advanced question patterns
        self.question_indicators = [
            r'\?',  # Question mark
            r'\bprove\b',
            r'\bshow\b',
            r'\bbuild\b',
            r'\bfind\b',
            r'\bexplain\b',
            r'\bdescribe\b',
            r'\bdraw\b',
            r'\bconstruct\b',
            r'\btrace\b',
            r'\bconvert\b',
        ]
    
    def detect_questions(self, text: str, 
                        min_length: int = 10,
                        max_length: int = 1000) -> List[Dict]:
        """
        Detect all questions in text
        
        Args:
            text: Text to analyze
            min_length: Minimum question length
            max_length: Maximum question length
            
        Returns:
            List of detected questions with metadata
        """
        questions = []
        
        # Method 1: Pattern-based extraction
        pattern_questions = self.pattern_matcher.extract_all_questions(text)
        
        for q in pattern_questions:
            question_text = q['text'].strip()
            
            # Filter by length
            if min_length <= len(question_text) <= max_length:
                # Classify question
                q_type = self.classifier.classify(question_text)
                metadata = self.classifier.get_question_metadata(question_text)
                
                questions.append({
                    'question': question_text,
                    'type': q_type.value,
                    'detection_method': 'pattern',
                    'metadata': metadata,
                    'location': {
                        'start': q['start'],
                        'end': q['end']
                    }
                })
        
        # Method 2: Sentence-based detection
        sentence_questions = self._detect_by_sentences(text, min_length, max_length)
        
        # Merge and deduplicate
        all_questions = self._merge_questions(questions, sentence_questions)
        
        return all_questions
    
    def _detect_by_sentences(self, text: str, 
                            min_length: int,
                            max_length: int) -> List[Dict]:
        """Detect questions by analyzing sentences"""
        questions = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            
            if min_length <= len(sentence) <= max_length:
                # Check if sentence contains question indicators
                if self._is_likely_question(sentence):
                    q_type = self.classifier.classify(sentence)
                    metadata = self.classifier.get_question_metadata(sentence)
                    
                    questions.append({
                        'question': sentence,
                        'type': q_type.value,
                        'detection_method': 'sentence',
                        'metadata': metadata,
                        'location': {
                            'sentence_index': i
                        }
                    })
        
        return questions
    
    def _is_likely_question(self, text: str) -> bool:
        """Check if text is likely a question"""
        text_lower = text.lower()
        
        # Check for question indicators
        for indicator in self.question_indicators:
            if re.search(indicator, text_lower):
                return True
        
        return False
    
    def _merge_questions(self, list1: List[Dict], list2: List[Dict]) -> List[Dict]:
        """Merge and deduplicate question lists"""
        all_questions = list1 + list2
        
        # Deduplicate based on question text
        seen = set()
        unique_questions = []
        
        for q in all_questions:
            question_normalized = q['question'].lower().strip()
            
            if question_normalized not in seen:
                seen.add(question_normalized)
                unique_questions.append(q)
        
        return unique_questions
    
    def extract_from_file(self, file_path: str) -> List[Dict]:
        """Extract questions from a file"""
        from ..utils.pdf_extractor import DocumentProcessor
        
        processor = DocumentProcessor()
        return processor.extract_questions_from_document(file_path)
