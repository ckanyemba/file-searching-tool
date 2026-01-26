#!/usr/bin/env python3
"""
Add Diagram Similarity Matching for PDAs
Uses computer vision to compare diagram structures
"""

from pathlib import Path

# ============================================================
# 1. Enhanced PDF Extractor with Diagram Extraction
# ============================================================

enhanced_pdf_extractor = '''"""
Enhanced PDF Extractor with Diagram Extraction
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF not installed")

try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("PIL not installed")

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV not installed - diagram matching disabled")


class DiagramExtractor:
    """Extract and process diagrams from PDFs"""
    
    def __init__(self, output_dir='database/diagrams'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_images_from_page(self, page, page_num: int, pdf_path: str) -> List[Dict]:
        """Extract all images from a PDF page"""
        images = []
        
        if not HAS_PYMUPDF or not HAS_PIL:
            return images
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert to PIL Image
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                # Save image
                img_filename = f"{Path(pdf_path).stem}_p{page_num}_img{img_index}.png"
                img_path = self.output_dir / img_filename
                pil_image.save(img_path)
                
                # Check if it looks like a diagram
                is_diagram = self.is_likely_diagram(pil_image)
                
                images.append({
                    'page': page_num,
                    'index': img_index,
                    'path': str(img_path),
                    'size': pil_image.size,
                    'is_diagram': is_diagram,
                    'hash': self.image_hash(pil_image)
                })
                
        except Exception as e:
            logger.error(f"Error extracting images from page {page_num}: {e}")
        
        return images
    
    def is_likely_diagram(self, image: Image.Image) -> bool:
        """Heuristic to determine if image is a diagram"""
        # Simple heuristics:
        # - Diagrams are often larger than small icons
        # - Have certain aspect ratios
        # - Not too colorful (PDAs are usually black/white line drawings)
        
        width, height = image.size
        
        # Size check
        if width < 100 or height < 100:
            return False
        
        # Convert to grayscale and check if mostly line art
        if HAS_CV2:
            import numpy as np
            img_array = np.array(image.convert('L'))
            unique_colors = len(np.unique(img_array))
            
            # Diagrams typically have few unique colors
            if unique_colors > 50:
                return False
        
        return True
    
    def image_hash(self, image: Image.Image) -> str:
        """Generate perceptual hash for image"""
        # Simple approach: resize and hash
        img_resized = image.resize((8, 8), Image.Resampling.LANCZOS)
        img_gray = img_resized.convert('L')
        pixels = list(img_gray.getdata())
        
        avg = sum(pixels) / len(pixels)
        bits = ''.join('1' if p > avg else '0' for p in pixels)
        
        return hex(int(bits, 2))[2:]


class DocumentProcessor:
    """Enhanced document processor with diagram support"""
    
    def __init__(self):
        self.question_patterns = [
            r'\\b\\d+\\.\\s+.*?(?:[.?]|$)',
            r'Example\\s+\\d+.*?(?=Example|$)',
            r'Draw.*?(?:PDA|DPDA|automaton|machine|FA|TM).*?(?:[.?]|(?=\\n\\n))',
            r'Build.*?(?:PDA|DPDA|TM|FA|automaton).*?(?:[.?]|(?=\\n\\n))',
            r'Construct.*?(?:PDA|DPDA|TM|FA).*?(?:[.?]|(?=\\n\\n))',
            r'L\\s*=\\s*\\{[^}]+\\}',
            r'Σ\\s*=\\s*\\{[^}]+\\}',
            r'\\bProve that.*?[.]',
            r'\\bShow that.*?[.]',
        ]
        
        self.diagram_extractor = DiagramExtractor()
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Enhanced PDF extraction with diagrams"""
        if not HAS_PYMUPDF:
            return None
        
        text_content = []
        all_diagrams = []
        
        try:
            doc = fitz.open(file_path)
            
            for page_num, page in enumerate(doc):
                # Extract text
                text = page.get_text()
                
                if text.strip():
                    text_content.append({
                        'page': page_num + 1,
                        'text': text,
                        'source': 'direct'
                    })
                
                # Extract diagrams
                diagrams = self.diagram_extractor.extract_images_from_page(
                    page, page_num + 1, file_path
                )
                all_diagrams.extend(diagrams)
            
            doc.close()
            
            return {
                'file_path': file_path,
                'file_type': 'pdf',
                'text_content': text_content,
                'diagrams': all_diagrams
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
        """Clean mathematical notation"""
        text = re.sub(r'\\s+', ' ', text)
        replacements = {
            '∑': 'Sigma', 'Σ': 'Sigma', '∈': 'in',
            '≥': '>=', '≤': '<=', '≠': '!=',
            '→': '->', '⇒': '=>', 'ε': 'epsilon',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def detect_questions(self, text: str) -> List[str]:
        """Detect questions"""
        text_clean = self.clean_mathematical_text(text)
        questions = []
        
        for pattern in self.question_patterns:
            matches = re.finditer(pattern, text_clean, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            for match in matches:
                question = match.group(0).strip()
                if 15 < len(question) < 500:
                    questions.append(question)
        
        # Extract Example blocks
        example_pattern = r'Example\\s+\\d+\\s*([\\s\\S]{20,400}?)(?=Example\\s+\\d+|$)'
        for match in re.finditer(example_pattern, text_clean, re.IGNORECASE):
            questions.append(match.group(0).strip())
        
        return list(set(questions))
    
    def extract_questions_from_document(self, file_path: str) -> List[Dict]:
        """Extract questions with diagram associations"""
        doc_data = self.process_file(file_path)
        if not doc_data:
            return []
        
        all_questions = []
        diagrams_by_page = {}
        
        # Index diagrams by page
        for diagram in doc_data.get('diagrams', []):
            page = diagram['page']
            if page not in diagrams_by_page:
                diagrams_by_page[page] = []
            diagrams_by_page[page].append(diagram)
        
        # Extract questions and associate with diagrams
        for content in doc_data.get('text_content', []):
            text = content.get('text', '')
            page = content.get('page')
            questions = self.detect_questions(text)
            
            # Get diagrams on this page
            page_diagrams = diagrams_by_page.get(page, [])
            
            for q in questions:
                question_data = {
                    'question': q,
                    'file': file_path,
                    'location': content,
                    'type': 'text'
                }
                
                # Associate diagram if present
                if page_diagrams:
                    # Use first diagram on page (heuristic)
                    diagram = page_diagrams[0]
                    question_data['diagram'] = diagram['path']
                    question_data['diagram_hash'] = diagram['hash']
                    question_data['has_diagram'] = True
                
                all_questions.append(question_data)
        
        return all_questions
'''

# ============================================================
# 2. Diagram Similarity Engine
# ============================================================

diagram_similarity_engine = '''"""
Diagram Similarity Engine
Compare PDA diagram structures using computer vision
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from skimage.metrics import structural_similarity as ssim
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False


class DiagramSimilarity:
    """Compare diagram similarity using various methods"""
    
    def __init__(self):
        self.methods_available = {
            'hash': True,  # Always available
            'histogram': HAS_PIL,
            'structural': HAS_CV2 and HAS_SKIMAGE,
            'feature': HAS_CV2,
        }
    
    def compare_diagrams(self, img1_path: str, img2_path: str) -> Dict[str, float]:
        """Compare two diagrams using multiple methods"""
        scores = {}
        
        if not Path(img1_path).exists() or not Path(img2_path).exists():
            return scores
        
        try:
            # Load images
            if HAS_PIL:
                img1_pil = Image.open(img1_path)
                img2_pil = Image.open(img2_path)
                
                # Hash similarity
                scores['hash'] = self.hash_similarity(img1_pil, img2_pil)
                
                # Histogram similarity
                if self.methods_available['histogram']:
                    scores['histogram'] = self.histogram_similarity(img1_pil, img2_pil)
            
            # OpenCV-based methods
            if HAS_CV2:
                img1_cv = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
                img2_cv = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
                
                if img1_cv is not None and img2_cv is not None:
                    # Structural similarity
                    if self.methods_available['structural']:
                        scores['structural'] = self.structural_similarity(img1_cv, img2_cv)
                    
                    # Feature matching
                    if self.methods_available['feature']:
                        scores['feature'] = self.feature_similarity(img1_cv, img2_cv)
            
            # Combined score
            if scores:
                scores['combined'] = np.mean(list(scores.values()))
            
        except Exception as e:
            logger.error(f"Error comparing diagrams: {e}")
        
        return scores
    
    def hash_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Perceptual hash similarity"""
        hash1 = self._perceptual_hash(img1)
        hash2 = self._perceptual_hash(img2)
        
        # Hamming distance
        distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        similarity = 1 - (distance / len(hash1))
        
        return similarity
    
    def _perceptual_hash(self, image: Image.Image, hash_size: int = 8) -> str:
        """Generate perceptual hash"""
        img = image.resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        img = img.convert('L')
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        return ''.join('1' if p > avg else '0' for p in pixels)
    
    def histogram_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Compare histograms"""
        img1_gray = img1.convert('L')
        img2_gray = img2.convert('L')
        
        hist1 = img1_gray.histogram()
        hist2 = img2_gray.histogram()
        
        # Normalize histograms
        hist1 = np.array(hist1) / sum(hist1)
        hist2 = np.array(hist2) / sum(hist2)
        
        # Correlation
        correlation = np.corrcoef(hist1, hist2)[0, 1]
        
        return max(0, correlation)  # Ensure non-negative
    
    def structural_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Structural similarity index (SSIM)"""
        if not HAS_SKIMAGE:
            return 0.0
        
        # Resize to same dimensions
        size = (256, 256)
        img1_resized = cv2.resize(img1, size)
        img2_resized = cv2.resize(img2, size)
        
        score, _ = ssim(img1_resized, img2_resized, full=True)
        
        return float(score)
    
    def feature_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Feature-based similarity using ORB"""
        try:
            orb = cv2.ORB_create()
            
            kp1, des1 = orb.detectAndCompute(img1, None)
            kp2, des2 = orb.detectAndCompute(img2, None)
            
            if des1 is None or des2 is None:
                return 0.0
            
            # Match features
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            
            # Similarity based on match ratio
            max_matches = min(len(kp1), len(kp2))
            if max_matches == 0:
                return 0.0
            
            similarity = len(matches) / max_matches
            
            return min(1.0, similarity)
        
        except Exception as e:
            logger.error(f"Feature matching error: {e}")
            return 0.0


class DiagramSearchEngine:
    """Search engine with diagram similarity"""
    
    def __init__(self):
        self.diagram_similarity = DiagramSimilarity()
    
    def search_with_diagram(self, query_diagram_path: str, 
                           questions: List[Dict], 
                           top_k: int = 5) -> List[Dict]:
        """Search for similar diagrams"""
        results = []
        
        for q in questions:
            if 'diagram' not in q or not q.get('has_diagram'):
                continue
            
            diagram_path = q['diagram']
            
            # Compare diagrams
            scores = self.diagram_similarity.compare_diagrams(
                query_diagram_path, 
                diagram_path
            )
            
            if scores and scores.get('combined', 0) > 0.3:
                result = {
                    **q,
                    'diagram_scores': scores,
                    'diagram_similarity': scores.get('combined', 0)
                }
                results.append(result)
        
        # Sort by diagram similarity
        results.sort(key=lambda x: x['diagram_similarity'], reverse=True)
        
        return results[:top_k]
'''

# ============================================================
# Write files
# ============================================================

files = {
    'src/utils/pdf_extractor.py': enhanced_pdf_extractor,
    'src/core/diagram_similarity.py': diagram_similarity_engine,
}

for path, content in files.items():
    Path(path).write_text(content)
    print(f"✓ Created {path}")

# Update requirements
requirements_add = '''
# Diagram matching dependencies
opencv-python>=4.8.0
scikit-image>=0.21.0
Pillow>=10.0.0
'''

with open('requirements.txt', 'a') as f:
    f.write('\n' + requirements_add)

print("\n" + "="*60)
print("✓ Diagram Similarity Matching Added!")
print("="*60)
print("\nNew capabilities:")
print("  ✅ Extract diagrams from PDFs")
print("  ✅ Perceptual hashing")
print("  ✅ Histogram comparison")
print("  ✅ Structural similarity (SSIM)")
print("  ✅ Feature matching (ORB)")
print("  ✅ Combined similarity score")
print("\nInstall dependencies:")
print("  pip install opencv-python scikit-image")
print("\nRebuild index:")
print("  python3 main.py --rebuild")
print("\nSearch by diagram:")
print("  Upload PDA diagram image in frontend")
print("  System finds visually similar PDAs")
print("="*60 + "\n")
