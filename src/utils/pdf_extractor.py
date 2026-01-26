"""
Enhanced Processor - Separates Questions and Solutions
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

try:
    import fitz
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


class QuestionSolutionDetector:
    """Detect and separate questions from solutions"""
    
    def __init__(self):
        # Patterns that indicate solutions section
        self.solution_markers = [
            r'\bSolutions?\b',
            r'\bAnswers?\b',
            r'\bMemo\b',
            r'\bSolution\s+to\b',
            r'\bAnswer\s+to\b',
            r'\bWorked\s+Solutions?\b',
            r'\bDetailed\s+Solutions?\b',
        ]
        
        # Question patterns
        self.question_patterns = [
            r'Question\s+\d+',
            r'Problem\s+\d+',
            r'Example\s+\d+',
            r'\b\d+\.\s+',
            r'\(([ivxlcdm]+)\)',
        ]
    
    def detect_section_type(self, text: str, page_num: int) -> str:
        """Detect if section contains questions or solutions"""
        text_lower = text.lower()
        
        # Check for solution markers
        for pattern in self.solution_markers:
            if re.search(pattern, text, re.IGNORECASE):
                return 'solution'
        
        # Heuristics for solutions:
        # - Contains "Therefore", "Hence", "Thus"
        # - Has step-by-step explanations
        # - References previous questions
        solution_indicators = [
            r'\btherefore\b',
            r'\bhence\b',
            r'\bthus\b',
            r'\bwe can see that\b',
            r'\bfrom the above\b',
            r'\bstep \d+',
            r'\bsolution:\b',
        ]
        
        solution_score = sum(1 for pattern in solution_indicators 
                           if re.search(pattern, text_lower))
        
        if solution_score >= 2:
            return 'solution'
        
        # Check if it looks like questions
        question_score = sum(1 for pattern in self.question_patterns 
                           if re.search(pattern, text, re.IGNORECASE))
        
        if question_score >= 1:
            return 'question'
        
        return 'unknown'
    
    def split_questions_solutions(self, pages_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Split pages into questions and solutions"""
        questions = []
        solutions = []
        
        current_section = 'question'  # Default to questions first
        
        for page_data in pages_data:
            text = page_data.get('text', '')
            page_num = page_data.get('page')
            
            # Detect section type
            section_type = self.detect_section_type(text, page_num)
            
            # Update current section if we found a clear marker
            if section_type != 'unknown':
                current_section = section_type
            
            # Add to appropriate list
            if current_section == 'question':
                questions.append(page_data)
            else:
                solutions.append(page_data)
        
        return questions, solutions


class DocumentProcessor:
    """Process documents with question/solution separation"""
    
    def __init__(self):
        self.detector = QuestionSolutionDetector()
        self.question_patterns = [
            r'Example\s+\d+.*?(?=Example|$)',
            r'Question\s+\d+.*?(?=Question|$)',
            r'Draw.*?(?:PDA|DPDA|automaton|machine|FA|TM).*?[.?]',
            r'Build.*?(?:PDA|TM|FA).*?[.?]',
            r'Prove.*?[.]',
            r'Show.*?[.]',
            r'Find.*?[.]',
            r'L\s*=\s*\{[^}]+\}',
        ]
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Extract with question/solution separation"""
        if not HAS_PYMUPDF:
            return None
        
        try:
            doc = fitz.open(file_path)
            pages_data = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    pages_data.append({
                        'page': page_num + 1,
                        'text': text,
                        'source': 'pdf'
                    })
            
            doc.close()
            
            # Split into questions and solutions
            questions_pages, solutions_pages = self.detector.split_questions_solutions(pages_data)
            
            return {
                'file_path': file_path,
                'file_type': 'pdf',
                'questions_pages': questions_pages,
                'solutions_pages': solutions_pages,
                'total_pages': len(pages_data)
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    def process_file(self, file_path: str) -> Dict:
        path = Path(file_path)
        if path.suffix.lower() == '.pdf':
            return self.extract_from_pdf(str(path))
        return None
    
    def detect_questions(self, text: str) -> List[str]:
        """Detect questions"""
        questions = []
        for pattern in self.question_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            for match in matches:
                q = match.group(0).strip()
                if 15 < len(q) < 500:
                    questions.append(q)
        return list(set(questions))
    
    def extract_questions_from_document(self, file_path: str) -> List[Dict]:
        """Extract questions AND solutions separately"""
        doc_data = self.process_file(file_path)
        if not doc_data:
            return []
        
        all_items = []
        
        # Process questions
        for page_data in doc_data.get('questions_pages', []):
            text = page_data.get('text', '')
            questions = self.detect_questions(text)
            
            for q in questions:
                all_items.append({
                    'question': q,
                    'file': file_path,
                    'location': page_data,
                    'type': 'question',
                    'section': 'questions'
                })
        
        # Process solutions
        for page_data in doc_data.get('solutions_pages', []):
            text = page_data.get('text', '')
            
            # Extract solution text (keep more context)
            solution_blocks = self.extract_solution_blocks(text)
            
            for solution in solution_blocks:
                all_items.append({
                    'question': solution,  # Solution text
                    'file': file_path,
                    'location': page_data,
                    'type': 'solution',
                    'section': 'solutions'
                })
        
        return all_items
    
    def extract_solution_blocks(self, text: str) -> List[str]:
        """Extract solution blocks"""
        # Split by question numbers
        pattern = r'(Question\s+\d+|Problem\s+\d+|Example\s+\d+|\d+\.)'
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        solutions = []
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                solution = parts[i] + parts[i+1]
                if len(solution.strip()) > 50:
                    solutions.append(solution.strip())
        
        return solutions if solutions else [text.strip()]
