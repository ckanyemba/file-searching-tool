#!/usr/bin/env python3
"""
Inspect what's actually in the index
"""

import pickle
from pathlib import Path
import json

print("\n" + "="*60)
print("Index Inspector")
print("="*60 + "\n")

# 1. Check the pickle file
data_file = Path('database/question_vectors/questions_data.pkl')

if not data_file.exists():
    print("✗ Index file not found!")
    print("  Run: python simple_main.py --rebuild")
    exit(1)

print("Loading index...")
with open(data_file, 'rb') as f:
    data = pickle.load(f)

questions = data.get('questions', [])
embeddings = data.get('embeddings')

print(f"✓ Found {len(questions)} questions in index")
if embeddings is not None:
    print(f"✓ Embeddings shape: {embeddings.shape}")

# 2. Show sample questions
print("\n" + "="*60)
print("Sample Questions in Index:")
print("="*60 + "\n")

for i, q in enumerate(questions[:20], 1):  # First 20
    question_text = q.get('question', 'NO TEXT')
    source = q.get('source', q.get('file', 'UNKNOWN'))
    
    print(f"{i}. {question_text[:100]}")
    print(f"   File: {source}")
    print()

# 3. Search for keywords
print("="*60)
print("Searching for Keywords in Questions:")
print("="*60 + "\n")

keywords = ['PDA', 'Example', 'Draw', 'deterministic', 'prove', 'palindrome']

for keyword in keywords:
    matches = [q for q in questions if keyword.lower() in q.get('question', '').lower()]
    print(f"'{keyword}': {len(matches)} matches")
    if matches and len(matches) <= 3:
        for m in matches:
            print(f"  - {m['question'][:80]}...")

# 4. Check question structure
print("\n" + "="*60)
print("Question Structure Check:")
print("="*60 + "\n")

if questions:
    sample = questions[0]
    print("Sample question object:")
    print(json.dumps(sample, indent=2))
    
    print("\nAll keys in questions:")
    all_keys = set()
    for q in questions[:100]:
        all_keys.update(q.keys())
    print(f"Keys: {sorted(all_keys)}")

# 5. Length statistics
print("\n" + "="*60)
print("Length Statistics:")
print("="*60 + "\n")

lengths = [len(q.get('question', '')) for q in questions]
print(f"Shortest: {min(lengths)} chars")
print(f"Longest: {max(lengths)} chars")
print(f"Average: {sum(lengths)/len(lengths):.1f} chars")

very_short = [q for q in questions if len(q.get('question', '')) < 20]
print(f"\nVery short (<20 chars): {len(very_short)}")
if very_short:
    for q in very_short[:5]:
        print(f"  '{q['question']}'")

print("\n" + "="*60)