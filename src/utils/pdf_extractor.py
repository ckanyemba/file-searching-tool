"""
Document Processing Module
Extracts text from PDF, DOCX, PPTX, and images
"""

import re
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from pptx import Presentation
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class DocumentProcessor:
    """Extract text and questions from various document formats"""
    
    def __init__(self):
        self.question_patterns = [
            r'\b\d+\.\s+.*?\?',
            r'\([ivxlcdm]+\)\s+.*?[.?]',
            r'Question\s+\d+:.*?[.?]',
            r'Problem\s+\d+:.*?[.?]',
            r'^[A-Z].*?\?$',
            r'\bProve that.*?[.]',
            r'\bShow that.*?[.]',
            r'\bBuild.*?[.]',
            r'\bDraw.*?[.]',
            r'\bFind.*?[.]',
        ]
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Extract text from PDF"""
        if not HAS_PYMUPDF:
            return None
        
        text_content = []
        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    text_content.append({
                        'page': page_num + 1,
                        'text': text,
                        'source': 'direct'
                    })
            doc.close()
            return {
                'file_path': file_path,
                'file_type': 'pdf',
                'text_content': text_content,
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    def process_file(self, file_path: str) -> Dict:
        """Process file based on extension"""
        path = Path(file_path)
        if path.suffix.lower() == '.pdf':
            return self.extract_from_pdf(str(path))
        return None
    
    def detect_questions(self, text: str) -> List[str]:
        """Detect questions in text"""
        questions = []
        for pattern in self.question_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                question = match.group(0).strip()
                if len(question) > 10:
                    questions.append(question)
        return list(set(questions))
    
    def extract_questions_from_document(self, file_path: str) -> List[Dict]:
        """Extract all questions from a document"""
        doc_data = self.process_file(file_path)
        if not doc_data:
            return []
        
        all_questions = []
        for content in doc_data.get('text_content', []):
            text = content.get('text', '')
            questions = self.detect_questions(text)
            
            for q in questions:
                all_questions.append({
                    'question': q,
                    'file': file_path,
                    'location': content,
                    'type': 'text'
                })
        
        return all_questions
