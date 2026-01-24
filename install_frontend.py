# Copy the entire code from the artifact above
#!/usr/bin/env python3
"""
Frontend Files Installer
Creates all frontend files in detection-tool/frontend/
"""

from pathlib import Path

print("\n" + "="*60)
print("Installing Frontend Files")
print("="*60 + "\n")

# Create frontend directory
frontend_dir = Path('frontend')
frontend_dir.mkdir(exist_ok=True)

# All frontend files
frontend_files = {

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
    <!-- Header -->
    <header class="header">
        <div class="container">
            <h1>🔍 COS3701 Question Search</h1>
            <div class="stats">
                <span>Questions: <strong id="totalQuestions">0</strong></span>
                <span>Files: <strong id="totalFiles">0</strong></span>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="main">
        <div class="container">
            <!-- Search Box -->
            <div class="search-box">
                <input 
                    type="text" 
                    id="searchInput" 
                    class="search-input" 
                    placeholder="Search for questions... (e.g., 'Prove that PALINDROME is non-context-free')"
                >
                <button id="searchBtn" class="search-btn">Search</button>
            </div>

            <!-- Options -->
            <div class="options">
                <div>
                    <label>Type:</label>
                    <select id="searchType">
                        <option value="semantic">Semantic</option>
                        <option value="exact">Exact</option>
                        <option value="typed">By Type</option>
                    </select>
                </div>
                <div>
                    <label>Results:</label>
                    <select id="topK">
                        <option value="5">5</option>
                        <option value="10">10</option>
                        <option value="20">20</option>
                    </select>
                </div>
            </div>

            <!-- Example Queries -->
            <div class="examples">
                <span>Try:</span>
                <button class="example-btn" data-query="Prove that PALINDROME is non-context-free">
                    Prove PALINDROME
                </button>
                <button class="example-btn" data-query="Build a TM that accepts {a^n b^n}">
                    Build TM
                </button>
                <button class="example-btn" data-query="Show that the language is regular">
                    Show regular
                </button>
            </div>

            <!-- Loading -->
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Searching...</p>
            </div>

            <!-- Results -->
            <div id="results" class="results"></div>

            <!-- Empty State -->
            <div id="emptyState" class="empty-state">
                <h2>Search COS3701 Questions</h2>
                <p>Enter a question or topic to find similar questions from past exams</p>
            </div>
        </div>
    </main>

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
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.header {
    background: #2563eb;
    color: white;
    padding: 1.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    font-size: 1.5rem;
}

.stats {
    display: flex;
    gap: 2rem;
}

.stats span {
    font-size: 0.9rem;
}

.stats strong {
    font-size: 1.2rem;
    margin-left: 0.5rem;
}

/* Main */
.main {
    padding: 2rem 0;
}

/* Search Box */
.search-box {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.search-input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 6px;
    font-size: 1rem;
}

.search-input:focus {
    outline: none;
    border-color: #2563eb;
}

.search-btn {
    padding: 0.75rem 2rem;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
}

.search-btn:hover {
    background: #1d4ed8;
}

/* Options */
.options {
    background: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
}

.options label {
    margin-right: 0.5rem;
    font-weight: 500;
}

.options select {
    padding: 0.5rem;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
}

/* Examples */
.examples {
    background: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

.examples span {
    margin-right: 1rem;
    font-weight: 500;
}

.example-btn {
    padding: 0.5rem 1rem;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    cursor: pointer;
    margin-right: 0.5rem;
    transition: all 0.2s;
}

.example-btn:hover {
    background: #2563eb;
    color: white;
    border-color: #2563eb;
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
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Results */
.results {
    margin-top: 2rem;
}

.result-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
    border-left: 4px solid #2563eb;
    transition: transform 0.2s;
}

.result-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.result-number {
    background: #2563eb;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.result-score {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
}

.score-high {
    background: #d1fae5;
    color: #065f46;
}

.score-medium {
    background: #fed7aa;
    color: #92400e;
}

.score-low {
    background: #fee2e2;
    color: #991b1b;
}

.result-question {
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 1rem;
    color: #1f2937;
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
    color: #6b7280;
}

.empty-state h2 {
    color: #1f2937;
    margin-bottom: 0.5rem;
}

/* Responsive */
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
    }
    
    .examples {
        text-align: center;
    }
    
    .example-btn {
        margin-bottom: 0.5rem;
    }
}
''',

# ============================================================
# frontend/app.js
# ============================================================
'frontend/app.js': '''// COS3701 Question Search - Frontend JavaScript

const API_URL = 'http://localhost:8000';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const searchType = document.getElementById('searchType');
const topK = document.getElementById('topK');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const emptyState = document.getElementById('emptyState');
const totalQuestions = document.getElementById('totalQuestions');
const totalFiles = document.getElementById('totalFiles');

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});

// Example buttons
document.querySelectorAll('.example-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        searchInput.value = e.target.dataset.query;
        handleSearch();
    });
});

// Load stats on page load
loadStats();

// Functions
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/api/stats`);
        const data = await response.json();
        
        totalQuestions.textContent = data.total_questions || 0;
        
        const fileCount = Object.keys(data.questions_by_file || {}).length;
        totalFiles.textContent = fileCount;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function handleSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    // Show loading
    loading.style.display = 'block';
    results.innerHTML = '';
    emptyState.style.display = 'none';
    
    try {
        const params = new URLSearchParams({
            query: query,
            search_type: searchType.value,
            top_k: topK.value
        });
        
        const response = await fetch(`${API_URL}/api/search?${params}`);
        const data = await response.json();
        
        displayResults(data.results, query);
    } catch (error) {
        console.error('Search error:', error);
        results.innerHTML = `
            <div class="result-card">
                <p style="color: #991b1b;">
                    ⚠️ Error: Could not connect to API server.
                    <br><br>
                    Make sure the server is running: <code>python3 src/api/app.py</code>
                </p>
            </div>
        `;
    } finally {
        loading.style.display = 'none';
    }
}

function displayResults(resultsList, query) {
    if (!resultsList || resultsList.length === 0) {
        results.innerHTML = `
            <div class="result-card">
                <p>No results found for "<strong>${escapeHtml(query)}</strong>"</p>
                <p style="margin-top: 1rem; color: #6b7280;">
                    Try a different search term or search type.
                </p>
            </div>
        `;
        return;
    }
    
    results.innerHTML = `
        <h2 style="margin-bottom: 1rem;">
            Found ${resultsList.length} results for "${escapeHtml(query)}"
        </h2>
    `;
    
    resultsList.forEach((result, index) => {
        const score = result.combined_score || 0;
        const scoreClass = score >= 0.8 ? 'score-high' : 
                          score >= 0.6 ? 'score-medium' : 'score-low';
        const scorePercent = (score * 100).toFixed(0);
        
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `
            <div class="result-header">
                <div class="result-number">${index + 1}</div>
                <div class="result-score ${scoreClass}">${scorePercent}% Match</div>
            </div>
            <div class="result-question">
                ${escapeHtml(result.question)}
            </div>
            <div class="result-meta">
                <span>📄 ${getFileName(result.file)}</span>
                ${result.location && result.location.page ? 
                    `<span>📖 Page ${result.location.page}</span>` : ''}
                ${result.question_type ? 
                    `<span>🏷️ ${result.question_type}</span>` : ''}
            </div>
        `;
        
        results.appendChild(card);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getFileName(path) {
    return path.split('/').pop().split('\\\\').pop();
}

// Check API health on load
fetch(`${API_URL}/api/health`)
    .then(res => res.json())
    .then(data => {
        console.log('API Status:', data.status);
    })
    .catch(err => {
        console.warn('API server not running. Start it with: python3 src/api/app.py');
    });
''',

}

# Create all files
print("Creating frontend files...\n")
created = 0

for filepath, content in frontend_files.items():
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"✓ {filepath}")
    created += 1

print(f"\n{'='*60}")
print(f"✓ Created {created} frontend files!")
print(f"{'='*60}")
print("\nTo use the frontend:")
print("1. Start the API server:")
print("   python3 src/api/app.py")
print("\n2. Open frontend/index.html in your browser")
print("   or run a local server:")
print("   cd frontend && python3 -m http.server 3000")
print(f"{'='*60}\n")