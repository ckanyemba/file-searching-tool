"""
Text cleaning and normalization utilities
"""

import re
import unicodedata


class TextCleaner:
    """Clean and normalize text for better matching"""
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra whitespace"""
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize unicode characters"""
        return unicodedata.normalize('NFKD', text)
    
    @staticmethod
    def remove_special_chars(text: str, keep_punctuation: bool = True) -> str:
        """Remove special characters"""
        if keep_punctuation:
            pattern = r'[^\w\s.,!?;:()\[\]{}\-\']'
        else:
            pattern = r'[^\w\s]'
        return re.sub(pattern, '', text)
    
    @staticmethod
    def normalize_numbers(text: str) -> str:
        """Normalize number representations"""
        # Convert superscripts
        superscripts = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
        text = text.translate(superscripts)
        
        # Convert subscripts
        subscripts = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
        text = text.translate(subscripts)
        
        return text
    
    @staticmethod
    def normalize_math_symbols(text: str) -> str:
        """Normalize mathematical symbols"""
        replacements = {
            '×': '*',
            '÷': '/',
            '≠': '!=',
            '≤': '<=',
            '≥': '>=',
            '→': '->',
            '⇒': '=>',
            '∈': 'in',
            '∪': 'union',
            '∩': 'intersection',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @classmethod
    def clean(cls, text: str, full_clean: bool = False) -> str:
        """Apply all cleaning steps"""
        text = cls.normalize_unicode(text)
        text = cls.remove_extra_whitespace(text)
        
        if full_clean:
            text = cls.normalize_numbers(text)
            text = cls.normalize_math_symbols(text)
        
        return text