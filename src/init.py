"""
COS3701 Question Search System
"""

__version__ = "1.0.0"
__author__ = "Craig Kanyemba"

from src.utils.pdf_extractor import DocumentProcessor
from src.core.similarity_engine import QuestionSimilarityEngine
from src.core.question_detector import QuestionDetector

__all__ = [
    'DocumentProcessor',
    'QuestionSimilarityEngine',
    'QuestionDetector',
]