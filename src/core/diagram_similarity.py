"""
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
