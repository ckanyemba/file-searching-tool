"""
Pattern matching for question detection
"""

import re
from typing import List, Dict, Tuple


class PatternMatcher:
    """Match and extract questions using regex patterns"""
    
    # Question number patterns
    NUMBERED_QUESTION = r'\b\d+\.\s+(.+?)(?=\n\d+\.|\n\n|$)'
    ROMAN_QUESTION = r'\(([ivxlcdm]+)\)\s+(.+?)(?=\n\([ivxlcdm]+\)|\n\n|$)'
    LETTER_QUESTION = r'\(([a-z])\)\s+(.+?)(?=\n\([a-z]\)|\n\n|$)'
    
    # Question keywords
    PROVE_PATTERN = r'\b(prove|show|demonstrate)\s+that\b.+?[.?]'
    BUILD_PATTERN = r'\b(build|construct|design|draw|create)\s+.+?[.?]'
    FIND_PATTERN = r'\b(find|determine|calculate|compute|give)\s+.+?[.?]'
    EXPLAIN_PATTERN = r'\b(explain|describe|discuss|define)\s+.+?[.?]'
    
    @classmethod
    def extract_numbered_questions(cls, text: str) -> List[Dict]:
        """Extract questions with numeric numbering (1., 2., etc.)"""
        matches = re.finditer(cls.NUMBERED_QUESTION, text, re.DOTALL | re.IGNORECASE)
        
        questions = []
        for match in matches:
            questions.append({
                'text': match.group(1).strip(),
                'number': match.group(0).split('.')[0].strip(),
                'type': 'numbered',
                'start': match.start(),
                'end': match.end()
            })
        
        return questions
    
    @classmethod
    def extract_roman_questions(cls, text: str) -> List[Dict]:
        """Extract questions with Roman numeral numbering (i), ii), etc.)"""
        matches = re.finditer(cls.ROMAN_QUESTION, text, re.DOTALL | re.IGNORECASE)
        
        questions = []
        for match in matches:
            questions.append({
                'text': match.group(2).strip(),
                'number': match.group(1),
                'type': 'roman',
                'start': match.start(),
                'end': match.end()
            })
        
        return questions
    
    @classmethod
    def extract_by_keyword(cls, text: str, pattern: str, 
                          keyword_type: str) -> List[Dict]:
        """Extract questions by keyword pattern"""
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        
        questions = []
        for match in matches:
            questions.append({
                'text': match.group(0).strip(),
                'keyword': keyword_type,
                'type': 'keyword',
                'start': match.start(),
                'end': match.end()
            })
        
        return questions
    
    @classmethod
    def extract_all_questions(cls, text: str) -> List[Dict]:
        """Extract all questions using all patterns"""
        all_questions = []
        
        # Numbered questions
        all_questions.extend(cls.extract_numbered_questions(text))
        
        # Roman numeral questions
        all_questions.extend(cls.extract_roman_questions(text))
        
        # Keyword-based questions
        keyword_patterns = [
            (cls.PROVE_PATTERN, 'prove'),
            (cls.BUILD_PATTERN, 'build'),
            (cls.FIND_PATTERN, 'find'),
            (cls.EXPLAIN_PATTERN, 'explain'),
        ]
        
        for pattern, keyword in keyword_patterns:
            all_questions.extend(
                cls.extract_by_keyword(text, pattern, keyword)
            )
        
        # Sort by position and remove duplicates
        all_questions.sort(key=lambda x: x['start'])
        
        # Remove overlapping questions
        unique_questions = []
        last_end = -1
        
        for q in all_questions:
            if q['start'] >= last_end:
                unique_questions.append(q)
                last_end = q['end']
        
        return unique_questions