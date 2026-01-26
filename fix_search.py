#!/usr/bin/env python3
"""
Fix search with lower threshold and debugging
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU

import pickle
import numpy as np
from pathlib import Path

print("\n" + "="*60)
print("Debug Search")
print("="*60 + "\n")

# Load index
data_file = Path('database/question_vectors/questions_data.pkl')
with open(data_file, 'rb') as f:
    data = pickle.load(f)

questions = data['questions']
embeddings = data['embeddings']

print(f"Loaded {len(questions)} questions\n")

# Load model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
print("Model loaded\n")

# Test query
query = "Draw a deterministic PDA"
print(f"Query: '{query}'\n")

# Encode query
query_embedding = model.encode([query])[0]

# Load FAISS index
try:
    import faiss
    index_file = Path('database/question_vectors/faiss_index.bin')
    index = faiss.read_index(str(index_file))
    
    # Search with more results
    k = min(20, len(questions))
    distances, indices = index.search(
        query_embedding.reshape(1, -1).astype('float32'), k
    )
    
    print(f"Top {k} results:\n")
    print("="*60)
    
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
        if idx < len(questions):
            q = questions[idx]
            
            # Calculate similarity score (closer distance = higher similarity)
            max_dist = max(distances[0]) if len(distances[0]) > 0 else 1.0
            similarity = 1 - (dist / (max_dist + 1e-6))
            
            print(f"\n{i}. Score: {similarity:.3f} (distance: {dist:.2f})")
            print(f"   {q['question'][:150]}")
            if len(q['question']) > 150:
                print("   ...")
            print(f"   File: {q.get('source', q.get('file', 'unknown'))}")
            
except ImportError:
    print("FAISS not installed - using numpy similarity")
    
    # Calculate cosine similarities
    from numpy.linalg import norm
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))
    
    similarities = []
    for i, emb in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, emb)
        similarities.append((sim, i))
    
    similarities.sort(reverse=True)
    
    print(f"Top 20 results:\n")
    print("="*60)
    
    for rank, (sim, idx) in enumerate(similarities[:20], 1):
        q = questions[idx]
        print(f"\n{rank}. Score: {sim:.3f}")
        print(f"   {q['question'][:150]}")
        if len(q['question']) > 150:
            print("   ...")
        print(f"   File: {q.get('source', q.get('file', 'unknown'))}")

# Also try basic keyword search
print("\n" + "="*60)
print("Keyword Matches:")
print("="*60 + "\n")

keywords = query.lower().split()
for keyword in keywords:
    matches = [q for q in questions if keyword in q['question'].lower()]
    print(f"'{keyword}': {len(matches)} matches")
    if matches:
        for m in matches[:3]:
            print(f"  - {m['question'][:100]}...")
        print()

print("="*60)