#!/usr/bin/env python3
"""
Complete Frontend with Image Search & Result Viewing
"""

from pathlib import Path

files = {

# ============================================================
# frontend/index.html
# ============================================================
'frontend/index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COS3701 Question Search</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>🔍 COS3701 Question Search</h1>
            <div class="stats">
                <span>Questions: <strong id="totalQuestions">0</strong></span>
                <span>Files: <strong id="totalFiles">0</strong></span>
            </div>
        </div>
    </header>

    <main class="main">
        <div class="container">
            <!-- Search Tabs -->
            <div class="tabs">
                <button class="tab active" data-tab="text">📝 Text Search</button>
                <button class="tab" data-tab="image">📷 Image Search</button>
            </div>

            <!-- Text Search -->
            <div id="textTab" class="tab-content active">
                <div class="search-box">
                    <textarea 
                        id="searchInput" 
                        class="search-input" 
                        placeholder="Type or paste your question here..."
                        rows="3"
                    ></textarea>
                    <button id="searchBtn" class="search-btn">🔍 Search</button>
                </div>
                <div class="examples">
                    <span>Examples:</span>
                    <button class="example-btn" data-query="Prove that PALINDROME is non-context-free">Prove PALINDROME</button>
                    <button class="example-btn" data-query="Build a TM that accepts {a^n b^n}">Build TM</button>
                    <button class="example-btn" data-query="Find a CFG for the language">Find CFG</button>
                </div>
            </div>

            <!-- Image Search -->
            <div id="imageTab" class="tab-content">
                <div class="upload-box">
                    <div class="upload-area" id="uploadArea">
                        <div class="upload-icon">📷</div>
                        <h3>Upload Question Image</h3>
                        <p>Take a photo or upload an image of the question</p>
                        <input type="file" id="imageInput" accept="image/*" capture="camera" hidden>
                        <button class="btn-primary" onclick="document.getElementById('imageInput').click()">
                            📸 Choose Image
                        </button>
                    </div>
                    
                    <div id="imagePreview" class="image-preview" style="display: none;">
                        <img id="previewImg" alt="Preview">
                        <div class="ocr-text" id="ocrText"></div>
                        <div class="btn-group">
                            <button id="clearBtn" class="btn-secondary">❌ Clear</button>
                            <button id="searchImageBtn" class="btn-primary">🔍 Search</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Options -->
            <div class="options">
                <label>Type: 
                    <select id="searchType">
                        <option value="semantic">Semantic</option>
                        <option value="exact">Exact</option>
                    </select>
                </label>
                <label>Results: 
                    <select id="topK">
                        <option value="5">5</option>
                        <option value="10">10</option>
                        <option value="20">20</option>
                    </select>
                </label>
            </div>

            <!-- Loading -->
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p id="loadingText">Searching...</p>
            </div>

            <!-- Results -->
            <div id="results"></div>

            <!-- Empty State -->
            <div id="emptyState" class="empty-state">
                <div class="empty-icon">🔍</div>
                <h2>Search Questions</h2>
                <p>Type a question or upload an image to find similar questions</p>
            </div>
        </div>
    </main>

    <!-- Result Modal -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Question Details</h2>
                <button class="modal-close">&times;</button>
            </div>
            <div id="modalBody" class="modal-body"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <script src="app.js"></script>
</body>
</html>
''',

# ============================================================
# frontend/style.css
# ============================================================
'frontend/style.css': '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f5;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    font-size: 1.75rem;
}

.stats {
    display: flex;
    gap: 2rem;
}

.stats strong {
    font-size: 1.3rem;
    margin-left: 0.5rem;
}

/* Tabs */
.tabs {
    display: flex;
    gap: 1rem;
    margin: 2rem 0 1.5rem;
}

.tab {
    padding: 0.75rem 1.5rem;
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s;
}

.tab.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

/* Search Box */
.search-box {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.search-input {
    flex: 1;
    padding: 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
}

.search-input:focus {
    outline: none;
    border-color: #667eea;
}

.search-btn {
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    white-space: nowrap;
}

.search-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Upload Box */
.upload-box {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.upload-area {
    border: 3px dashed #e5e7eb;
    border-radius: 12px;
    padding: 3rem;
    text-align: center;
    cursor: pointer;
}

.upload-area:hover {
    border-color: #667eea;
    background: #f9fafb;
}

.upload-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.upload-area h3 {
    margin-bottom: 0.5rem;
}

.upload-area p {
    color: #6b7280;
    margin-bottom: 1.5rem;
}

.image-preview {
    text-align: center;
}

.image-preview img {
    max-width: 100%;
    max-height: 400px;
    border-radius: 8px;
    margin-bottom: 1rem;
}

.ocr-text {
    background: #f9fafb;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    text-align: left;
    white-space: pre-wrap;
    border: 1px solid #e5e7eb;
    max-height: 200px;
    overflow-y: auto;
}

.btn-group {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

.btn-primary {
    padding: 0.75rem 2rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
}

.btn-primary:hover {
    background: #5568d3;
}

.btn-secondary {
    padding: 0.75rem 2rem;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    cursor: pointer;
}

/* Options */
.options {
    background: white;
    padding: 1rem 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    display: flex;
    gap: 2rem;
    margin-bottom: 1.5rem;
}

.options label {
    font-weight: 500;
}

.options select {
    margin-left: 0.5rem;
    padding: 0.5rem;
    border: 2px solid #e5e7eb;
    border-radius: 6px;
}

/* Examples */
.examples {
    background: white;
    padding: 1rem 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}

.examples span {
    font-weight: 600;
    margin-right: 1rem;
}

.example-btn {
    padding: 0.5rem 1rem;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    border-radius: 20px;
    cursor: pointer;
    margin-right: 0.5rem;
    font-size: 0.875rem;
}

.example-btn:hover {
    background: #667eea;
    color: white;
}

/* Loading */
.loading {
    text-align: center;
    padding: 3rem;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #f3f4f6;
    border-top-color: #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Results */
#results {
    margin-top: 2rem;
}

.result-card {
    background: white;
    padding: 1.75rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
    cursor: pointer;
    transition: all 0.3s;
}

.result-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.result-number {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.result-score {
    padding: 0.375rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
}

.score-high { background: #d1fae5; color: #065f46; }
.score-medium { background: #fed7aa; color: #92400e; }
.score-low { background: #fee2e2; color: #991b1b; }

.result-question {
    font-size: 1.1rem;
    line-height: 1.7;
    margin-bottom: 1rem;
}

.result-meta {
    display: flex;
    gap: 1.5rem;
    color: #6b7280;
    font-size: 0.875rem;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

/* Modal */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    z-index: 1000;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.modal.active {
    display: flex;
}

.modal-content {
    background: white;
    border-radius: 16px;
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #e5e7eb;
}

.modal-close {
    background: none;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    color: #6b7280;
}

.modal-body {
    padding: 2rem;
}

.detail-section {
    margin-bottom: 1.5rem;
}

.detail-label {
    font-weight: 600;
    color: #6b7280;
    font-size: 0.875rem;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.detail-content {
    font-size: 1.1rem;
    line-height: 1.7;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
}

@media (max-width: 768px) {
    .header .container {
        flex-direction: column;
        gap: 1rem;
    }
    .search-box {
        flex-direction: column;
    }
    .options {
        flex-direction: column;
        gap: 1rem;
    }
    .detail-grid {
        grid-template-columns: 1fr;
    }
}
''',

# ============================================================
# frontend/app.js
# ============================================================
'frontend/app.js': '''const API_URL = 'http://localhost:8000';

// Elements
const tabs = document.querySelectorAll('.tab');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const ocrText = document.getElementById('ocrText');
const clearBtn = document.getElementById('clearBtn');
const searchImageBtn = document.getElementById('searchImageBtn');
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loadingText');
const results = document.getElementById('results');
const emptyState = document.getElementById('emptyState');
const modal = document.getElementById('modal');
const modalBody = document.getElementById('modalBody');

let currentOcrText = '';

// Tab switching
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(tc => {
            tc.classList.remove('active');
        });
        document.getElementById(tab.dataset.tab + 'Tab').classList.add('active');
    });
});

// Text search
searchBtn.addEventListener('click', () => {
    const query = searchInput.value.trim();
    if (query) performSearch(query);
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        searchBtn.click();
    }
});

// Example buttons
document.querySelectorAll('.example-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        searchInput.value = e.target.dataset.query;
        searchBtn.click();
    });
});

// Image upload
imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleImage(file);
});

clearBtn.addEventListener('click', () => {
    imageInput.value = '';
    uploadArea.style.display = 'block';
    imagePreview.style.display = 'none';
    currentOcrText = '';
});

searchImageBtn.addEventListener('click', () => {
    if (currentOcrText) performSearch(currentOcrText);
});

// Modal
document.querySelector('.modal-close').addEventListener('click', () => {
    modal.classList.remove('active');
});

modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('active');
});

// Functions
async function handleImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadArea.style.display = 'none';
        imagePreview.style.display = 'block';
        extractText(e.target.result);
    };
    reader.readAsDataURL(file);
}

async function extractText(imageData) {
    try {
        showLoading('Extracting text from image...');
        
        const worker = await Tesseract.createWorker('eng');
        const { data: { text } } = await worker.recognize(imageData);
        await worker.terminate();
        
        currentOcrText = text.trim();
        ocrText.textContent = currentOcrText || 'No text detected';
        
        hideLoading();
    } catch (error) {
        console.error('OCR error:', error);
        ocrText.textContent = 'Error extracting text';
        hideLoading();
    }
}

async function performSearch(query) {
    showLoading('Searching...');
    results.innerHTML = '';
    emptyState.style.display = 'none';
    
    try {
        const params = new URLSearchParams({
            query: query,
            search_type: document.getElementById('searchType').value,
            top_k: document.getElementById('topK').value
        });
        
        const response = await fetch(`${API_URL}/api/search?${params}`);
        const data = await response.json();
        
        displayResults(data.results, query);
    } catch (error) {
        results.innerHTML = `
            <div class="result-card">
                <p style="color: #991b1b;">⚠️ Error: Cannot connect to server. 
                Start it with: <code>python3 src/api/app.py</code></p>
            </div>
        `;
    } finally {
        hideLoading();
    }
}

function displayResults(resultsList, query) {
    if (!resultsList || resultsList.length === 0) {
        results.innerHTML = `
            <div class="result-card">
                <p>No results found for "<strong>${escapeHtml(query)}</strong>"</p>
            </div>
        `;
        return;
    }
    
    results.innerHTML = `<h2>Found ${resultsList.length} results</h2>`;
    
    resultsList.forEach((result, i) => {
        const card = createResultCard(result, i + 1);
        results.appendChild(card);
    });
}

function createResultCard(result, num) {
    const score = result.combined_score || 0;
    const scoreClass = score >= 0.8 ? 'score-high' : score >= 0.6 ? 'score-medium' : 'score-low';
    
    const card = document.createElement('div');
    card.className = 'result-card';
    card.onclick = () => showDetail(result);
    
    card.innerHTML = `
        <div class="result-header">
            <div class="result-number">${num}</div>
            <div class="result-score ${scoreClass}">${(score * 100).toFixed(0)}% Match</div>
        </div>
        <div class="result-question">${escapeHtml(result.question)}</div>
        <div class="result-meta">
            <span>📄 ${getFileName(result.file)}</span>
            ${result.location && result.location.page ? `<span>📖 Page ${result.location.page}</span>` : ''}
        </div>
    `;
    
    return card;
}

function showDetail(result) {
    const score = result.combined_score || 0;
    
    modalBody.innerHTML = `
        <div class="detail-section">
            <div class="detail-label">Question</div>
            <div class="detail-content">${escapeHtml(result.question)}</div>
        </div>
        
        <div class="detail-grid">
            <div class="detail-section">
                <div class="detail-label">Source File</div>
                <div class="detail-content">${getFileName(result.file)}</div>
            </div>
            
            ${result.location && result.location.page ? `
            <div class="detail-section">
                <div class="detail-label">Page Number</div>
                <div class="detail-content">Page ${result.location.page}</div>
            </div>
            ` : ''}
            
            <div class="detail-section">
                <div class="detail-label">Match Score</div>
                <div class="detail-content">${(score * 100).toFixed(1)}%</div>
            </div>
            
            ${result.question_type ? `
            <div class="detail-section">
                <div class="detail-label">Question Type</div>
                <div class="detail-content" style="text-transform: capitalize;">${result.question_type}</div>
            </div>
            ` : ''}
        </div>
        
        <div class="detail-section" style="margin-top: 2rem;">
            <button class="btn-primary" onclick="copyToClipboard('${escapeHtml(result.question).replace(/'/g, "\\'")}')">
                📋 Copy Question
            </button>
        </div>
    `;
    
    modal.classList.add('active');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Question copied to clipboard!');
    });
}

function showLoading(text) {
    loadingText.textContent = text;
    loading.style.display = 'block';
}

function hideLoading() {
    loading.style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getFileName(path) {
    return path.split('/').pop().split('\\\\').pop();
}

// Load stats
fetch(`${API_URL}/api/stats`)
    .then(r => r.json())
    .then(data => {
        document.getElementById('totalQuestions').textContent = data.total_questions || 0;
        document.getElementById('totalFiles').textContent = Object.keys(data.questions_by_file || {}).length;
    })
    .catch(() => {});
''',

}

# Create files
for path, content in files.items():
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
    print(f"✓ {path}")

print("\n" + "="*60)
print("✓ Complete Frontend Installed!")
print("="*60)
print("\n1. Start API: python3 src/api/app.py")
print("2. Open: frontend/index.html")
print("   or run: cd frontend && python3 -m http.server 3000")
print("\nFeatures:")
print("  ✅ Text search")
print("  ✅ Image search with OCR")
print("  ✅ Beautiful results display")
print("  ✅ Click to view full details")
print("  ✅ Copy questions")
print("="*60 + "\n")
