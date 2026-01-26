#!/usr/bin/env python3
"""
Quick Fix Script
1. Force CPU mode
2. Test extraction
3. Build index with small batch
"""

import os
import sys
import json
from pathlib import Path

# FORCE CPU mode before any imports
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU
os.environ['TRANSFORMERS_OFFLINE'] = '0'

print("\n" + "="*60)
print("Quick Fix - Testing System")
print("="*60 + "\n")

# 1. Check what was extracted
print("1. Checking Extracted Questions...")
extracted_dir = Path('database/extracted_questions')

if not extracted_dir.exists():
    print("   ✗ No extracted_questions directory")
else:
    json_files = list(extracted_dir.glob('*.json'))
    print(f"   ✓ Found {len(json_files)} extracted files")
    
    total_questions = 0
    for json_file in json_files[:3]:  # Check first 3
        try:
            with open(json_file) as f:
                questions = json.load(f)
                print(f"   - {json_file.name}: {len(questions)} questions")
                
                # Show first question
                if questions:
                    first_q = questions[0]['question'][:100]
                    print(f"     Sample: {first_q}...")
                
                total_questions += len(questions)
        except Exception as e:
            print(f"   ✗ Error reading {json_file.name}: {e}")
    
    print(f"\n   Total: {total_questions} questions extracted")

# 2. Check master file
print("\n2. Checking Master Questions File...")
master_file = Path('database/questions_master.json')
if master_file.exists():
    with open(master_file) as f:
        data = json.load(f)
        print(f"   ✓ Master file: {len(data)} questions")
        
        # Show samples
        if data:
            print("\n   Samples:")
            for i, q in enumerate(data[:5], 1):
                print(f"   {i}. {q['question'][:80]}...")
else:
    print("   ✗ No master file found")

# 3. Now try to build index with CPU
print("\n3. Building Index (CPU mode)...")

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    # Load model on CPU
    print("   Loading model (CPU)...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    print("   ✓ Model loaded")
    
    # Load questions
    with open('database/questions_master.json') as f:
        questions = json.load(f)
    
    print(f"   Processing {len(questions)} questions...")
    
    # Encode in smaller batches to avoid memory issues
    texts = [q['question'] for q in questions]
    
    # Process in chunks
    batch_size = 32
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"   Batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...", end='\r')
        embeddings = model.encode(batch, show_progress_bar=False)
        all_embeddings.append(embeddings)
    
    embeddings = np.vstack(all_embeddings)
    print(f"\n   ✓ Created embeddings: {embeddings.shape}")
    
    # Build FAISS index
    try:
        import faiss
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        # Save
        vectors_dir = Path('database/question_vectors')
        vectors_dir.mkdir(exist_ok=True)
        
        index_file = vectors_dir / 'faiss_index.bin'
        faiss.write_index(index, str(index_file))
        print(f"   ✓ Saved FAISS index: {index_file}")
        
        # Save data
        import pickle
        data_file = vectors_dir / 'questions_data.pkl'
        with open(data_file, 'wb') as f:
            pickle.dump({
                'questions': questions,
                'embeddings': embeddings
            }, f)
        print(f"   ✓ Saved questions data: {data_file}")
        
        print("\n✓ INDEX BUILT SUCCESSFULLY!")
        
    except ImportError:
        print("   ⚠️  FAISS not installed - basic search only")
        
        # Save data without FAISS
        import pickle
        vectors_dir = Path('database/question_vectors')
        vectors_dir.mkdir(exist_ok=True)
        
        data_file = vectors_dir / 'questions_data.pkl'
        with open(data_file, 'wb') as f:
            pickle.dump({
                'questions': questions,
                'embeddings': embeddings
            }, f)
        print(f"   ✓ Saved questions data: {data_file}")
        print("\n✓ Data saved (install faiss-cpu for vector search)")
        
except ImportError as e:
    print(f"   ✗ Missing dependency: {e}")
    print("\n   Install: pip install sentence-transformers")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 4. Test search
print("\n4. Testing Search...")
try:
    from simple_main import SimpleQuestionSearcher
    
    searcher = SimpleQuestionSearcher()
    if searcher.load_index():
        print(f"   ✓ Loaded {len(searcher.questions)} questions")
        
        # Test query
        test_query = "prove palindrome"
        print(f"\n   Testing: '{test_query}'")
        results = searcher.search(test_query, top_k=3)
        
        if results:
            print(f"   ✓ Found {len(results)} results:")
            for i, r in enumerate(results, 1):
                print(f"   {i}. {r['question'][:70]}...")
                print(f"      Score: {r['score']:.2%}")
        else:
            print("   ⚠️  No results - trying basic search...")
            results = searcher.search_basic(test_query, top_k=3)
            if results:
                print(f"   ✓ Basic search found {len(results)} results")
    else:
        print("   ✗ Could not load index")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("\nIf index was built successfully, you can now:")
print("  1. Search: python simple_main.py --query 'your question'")
print("  2. Interactive: python simple_main.py")
print("  3. API: python src/api/app.py")
print("="*60 + "\n")