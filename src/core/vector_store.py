"""
Vector storage and retrieval using FAISS
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage vector embeddings with FAISS"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.metadata = []
        
    def create_index(self, use_gpu: bool = False):
        """Create a new FAISS index"""
        if use_gpu and faiss.get_num_gpus() > 0:
            logger.info("Using GPU for FAISS index")
            res = faiss.StandardGpuResources()
            self.index = faiss.GpuIndexFlatL2(res, self.dimension)
        else:
            logger.info("Using CPU for FAISS index")
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict]):
        """Add vectors to the index"""
        if self.index is None:
            self.create_index()
        
        vectors_float32 = vectors.astype('float32')
        self.index.add(vectors_float32)
        self.metadata.extend(metadata)
        
        logger.info(f"Added {len(vectors)} vectors to index")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """Search for k nearest neighbors"""
        if self.index is None:
            raise ValueError("Index not created. Call create_index() first.")
        
        query_float32 = query_vector.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_float32, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'distance': float(dist),
                    'metadata': self.metadata[idx]
                })
        
        return results
    
    def save(self, index_path: str, metadata_path: str):
        """Save index and metadata to disk"""
        index_path = Path(index_path)
        metadata_path = Path(metadata_path)
        
        # Create directories if needed
        index_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        logger.info(f"Saved index to {index_path}")
    
    def load(self, index_path: str, metadata_path: str):
        """Load index and metadata from disk"""
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        
        logger.info(f"Loaded index from {index_path}")