"""
Text cleaning utilities
"""

import re
import unicodedata


class TextCleaner:
    """Clean and normalize text"""
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        return unicodedata.normalize('NFKD', text)
    
    @staticmethod
    def clean(text: str, full_clean: bool = False) -> str:
        text = TextCleaner.normalize_unicode(text)
        text = TextCleaner.remove_extra_whitespace(text)
        return text
