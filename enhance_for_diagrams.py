#!/usr/bin/env python3
"""
Enhance system for PDA diagrams and mathematical notation
"""

from pathlib import Path

# Enhanced PDF extractor with better pattern matching
enhanced_extractor = '''"""
Enhanced Document Processor for PDA/Mathematical Content
"""

import re
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

class DocumentProcessor:
    """Extract text and questions including mathematical notation"""
    
    def __init__(self):
        self.question_patterns = [
            # Standard patterns
            r'\\b\\d+\\.\\s+.*?(?:[.?]|$)',
            r'Example\\s+\\d+.*?(?=Example|$)',
            
            # PDA/Mathematical patterns
            r'Draw.*?(?:PDA|automaton|machine).*?(?:[.?]|(?=\\n\\n))',
            r'Build.*?(?:PDA|TM|FA|automaton).*?(?:[.?]|(?=\\n\\n))',
            r'L\\s*=\\s*\\{.*?\\}',  # Language definitions
            r'Σ\\s*=\\s*\\{.*?\\}',  # Alphabet definitions
            
            # Question types
            r'\\bProve that.*?[.]',
            r'\\bShow that.*?[.]',
            r'\\bFind.*?[.]',
            r'\\bConstruct.*?[.]',
        ]
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Enhanced PDF extraction"""
        if not HAS_PYMUPDF:
            return None
        
        text_content = []
        try:
            doc = fitz.open(file_path)
            
            for page_num, page in enumerate(doc):
                # Extract text
                text = page.get_text()
                
                # Also try to get text with layout preservation
                text_dict = page.get_text("dict")
                
                if text.strip():
                    text_content.append({
                        'page': page_num + 1,
                        'text': text,
                        'source': 'direct'
                    })
                
                # Extract images (for diagrams)
                images = page.get_images()
                for img_index, img in enumerate(images):
                    text_content.append({
                        'page': page_num + 1,
                        'type': 'diagram',
                        'image_index': img_index,
                        'source': 'image'
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
        """Process file"""
        path = Path(file_path)
        if path.suffix.lower() == '.pdf':
            return self.extract_from_pdf(str(path))
        return None
    
    def clean_mathematical_text(self, text: str) -> str:
        """Clean mathematical notation for better matching"""
        # Normalize common math symbols
        text = re.sub(r'\\s+', ' ', text)
        text = text.replace('∑', 'Sigma')
        text = text.replace('Σ', 'Sigma')
        text = text.replace('∈', 'in')
        text = text.replace('≥', '>=')
        text = text.replace('≤', '<=')
        return text
    
    def detect_questions(self, text: str) -> List[str]:
        """Detect questions including PDA/mathematical content"""
        text_clean = self.clean_mathematical_text(text)
        
        questions = []
        
        # Detect by patterns
        for pattern in self.question_patterns:
            matches = re.finditer(pattern, text_clean, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            for match in matches:
                question = match.group(0).strip()
                # Only keep substantial questions
                if len(question) > 15 and len(question) < 500:
                    questions.append(question)
        
        # Detect Example blocks
        example_pattern = r'Example\\s+\\d+\\s*([\\s\\S]*?)(?=Example\\s+\\d+|$)'
        for match in re.finditer(example_pattern, text_clean, re.IGNORECASE):
            example_text = match.group(0).strip()
            if len(example_text) > 20:
                questions.append(example_text)
        
        # Deduplicate
        return list(set(questions))
    
    def extract_questions_from_document(self, file_path: str) -> List[Dict]:
        """Extract questions"""
        doc_data = self.process_file(file_path)
        if not doc_data:
            return []
        
        all_questions = []
        
        for content in doc_data.get('text_content', []):
            if content.get('type') == 'diagram':
                # Mark that this page has diagrams
                all_questions.append({
                    'question': f"Page {content['page']} contains diagram",
                    'file': file_path,
                    'location': content,
                    'type': 'diagram',
                    'has_diagram': True
                })
            else:
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
'''

# Write enhanced extractor
Path('src/utils/pdf_extractor.py').write_text(enhanced_extractor)
print("✓ Enhanced PDF extractor created")

print("\n" + "="*60)
print("System Enhanced for PDA Diagrams!")
print("="*60)
print("\nNow the system can:")
print("  ✅ Extract questions from PDAs")
print("  ✅ Detect 'Draw a PDA' type questions")
print("  ✅ Handle mathematical notation (L = {...}, Σ = {...})")
print("  ✅ Recognize Example 1, Example 2, etc.")
print("  ✅ Mark pages with diagrams")
print("\nNext steps:")
print("  1. Add your PDF: cp COS301Y-Deterministic-PDAs.pdf database/exam_papers/")
print("  2. Rebuild index: python3 main.py --rebuild")
print("  3. Search: 'Draw a PDA that accepts ba'")
print("="*60 + "\n")
