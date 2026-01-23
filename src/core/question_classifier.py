"""
Question type classification
"""

import re
from typing import Dict, List
from enum import Enum


class QuestionType(Enum):
    """Question type enumeration"""
    PROOF = "proof"
    BUILD = "build"
    FIND = "find"
    EXPLAIN = "explain"
    TRACE = "trace"
    CONVERT = "convert"
    TRUE_FALSE = "true_false"
    MULTIPLE_CHOICE = "multiple_choice"
    SHOW = "show"
    DRAW = "draw"
    GENERAL = "general"


class QuestionClassifier:
    """Classify questions by type"""
    
    # Classification patterns
    PATTERNS = {
        QuestionType.PROOF: [
            r'\bprove\b',
            r'\bproof\b',
            r'\bdemonstrate\b',
        ],
        QuestionType.SHOW: [
            r'\bshow\s+that\b',
            r'\bshow\s+how\b',
        ],
        QuestionType.BUILD: [
            r'\bbuild\b',
            r'\bconstruct\b',
            r'\bdesign\b',
            r'\bcreate\b',
        ],
        QuestionType.DRAW: [
            r'\bdraw\b',
            r'\bsketch\b',
            r'\bdiagram\b',
        ],
        QuestionType.FIND: [
            r'\bfind\b',
            r'\bdetermine\b',
            r'\bcalculate\b',
            r'\bcompute\b',
        ],
        QuestionType.EXPLAIN: [
            r'\bexplain\b',
            r'\bdescribe\b',
            r'\bdiscuss\b',
            r'\bdefine\b',
        ],
        QuestionType.TRACE: [
            r'\btrace\b',
            r'\bfollow\b',
            r'\btrack\b',
        ],
        QuestionType.CONVERT: [
            r'\bconvert\b',
            r'\btransform\b',
            r'\btranslate\b',
        ],
        QuestionType.TRUE_FALSE: [
            r'\btrue\s+or\s+false\b',
            r'\bis\s+it\s+true\b',
        ],
        QuestionType.MULTIPLE_CHOICE: [
            r'\([a-d]\)',
            r'\boption\s+[a-d]\b',
        ],
    }
    
    @classmethod
    def classify(cls, question: str) -> QuestionType:
        """Classify a question by type"""
        question_lower = question.lower()
        
        for q_type, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower, re.IGNORECASE):
                    return q_type
        
        return QuestionType.GENERAL
    
    @classmethod
    def get_question_metadata(cls, question: str) -> Dict:
        """Get comprehensive metadata about a question"""
        q_type = cls.classify(question)
        
        metadata = {
            'type': q_type.value,
            'length': len(question),
            'word_count': len(question.split()),
            'has_question_mark': '?' in question,
            'starts_with_capital': question[0].isupper() if question else False,
        }
        
        return metadata