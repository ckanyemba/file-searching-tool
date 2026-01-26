#!/usr/bin/env python3
"""
Add Questions & Solutions Tab System
Automatically detects and separates questions from solutions
"""

from pathlib import Path

# ============================================================
# 1. Enhanced PDF Processor - Detect Questions & Solutions
# ============================================================

enhanced_processor = '''"""
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
            r'\\bSolutions?\\b',
            r'\\bAnswers?\\b',
            r'\\bMemo\\b',
            r'\\bSolution\\s+to\\b',
            r'\\bAnswer\\s+to\\b',
            r'\\bWorked\\s+Solutions?\\b',
            r'\\bDetailed\\s+Solutions?\\b',
        ]
        
        # Question patterns
        self.question_patterns = [
            r'Question\\s+\\d+',
            r'Problem\\s+\\d+',
            r'Example\\s+\\d+',
            r'\\b\\d+\\.\\s+',
            r'\\(([ivxlcdm]+)\\)',
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
            r'\\btherefore\\b',
            r'\\bhence\\b',
            r'\\bthus\\b',
            r'\\bwe can see that\\b',
            r'\\bfrom the above\\b',
            r'\\bstep \\d+',
            r'\\bsolution:\\b',
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
            r'Example\\s+\\d+.*?(?=Example|$)',
            r'Question\\s+\\d+.*?(?=Question|$)',
            r'Draw.*?(?:PDA|DPDA|automaton|machine|FA|TM).*?[.?]',
            r'Build.*?(?:PDA|TM|FA).*?[.?]',
            r'Prove.*?[.]',
            r'Show.*?[.]',
            r'Find.*?[.]',
            r'L\\s*=\\s*\\{[^}]+\\}',
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
        pattern = r'(Question\\s+\\d+|Problem\\s+\\d+|Example\\s+\\d+|\\d+\\.)'
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        solutions = []
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                solution = parts[i] + parts[i+1]
                if len(solution.strip()) > 50:
                    solutions.append(solution.strip())
        
        return solutions if solutions else [text.strip()]
'''

# ============================================================
# 2. Enhanced API with Questions/Solutions endpoints
# ============================================================

api_enhancement = '''
# Add these endpoints to src/api/app.py

@app.route('/api/questions', methods=['GET'])
def get_questions_only():
    """Get only questions (no solutions)"""
    try:
        if not search_system or not search_system.all_questions:
            return jsonify({'questions': [], 'total': 0})
        
        questions = [
            q for q in search_system.all_questions 
            if q.get('section') == 'questions'
        ]
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'questions': questions[start:end],
            'total': len(questions),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/solutions', methods=['GET'])
def get_solutions_only():
    """Get only solutions"""
    try:
        if not search_system or not search_system.all_questions:
            return jsonify({'solutions': [], 'total': 0})
        
        solutions = [
            q for q in search_system.all_questions 
            if q.get('section') == 'solutions'
        ]
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'solutions': solutions[start:end],
            'total': len(solutions),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/questions', methods=['GET'])
def search_questions_only():
    """Search only in questions"""
    query = request.args.get('query', '')
    top_k = int(request.args.get('top_k', 5))
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        # Filter to questions only
        questions_only = [
            q for q in search_system.all_questions
            if q.get('section') == 'questions'
        ]
        
        # Create temporary search engine for questions
        temp_engine = search_system.search_engine
        temp_engine.questions = questions_only
        
        results = temp_engine.search(query, top_k=top_k)
        
        return jsonify({
            'query': query,
            'results': results,
            'total': len(results),
            'section': 'questions'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/solutions', methods=['GET'])
def search_solutions_only():
    """Search only in solutions"""
    query = request.args.get('query', '')
    top_k = int(request.args.get('top_k', 5))
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        # Filter to solutions only
        solutions_only = [
            q for q in search_system.all_questions
            if q.get('section') == 'solutions'
        ]
        
        temp_engine = search_system.search_engine
        temp_engine.questions = solutions_only
        
        results = temp_engine.search(query, top_k=top_k)
        
        return jsonify({
            'query': query,
            'results': results,
            'total': len(results),
            'section': 'solutions'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''

# ============================================================
# 3. Enhanced Frontend with Questions/Solutions Tabs
# ============================================================

enhanced_frontend = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COS3701 - Questions & Solutions</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>🔍 COS3701 Question Search</h1>
            <div class="stats">
                <span>Questions: <strong id="totalQuestions">0</strong></span>
                <span>Solutions: <strong id="totalSolutions">0</strong></span>
            </div>
        </div>
    </header>

    <main class="main">
        <div class="container">
            <!-- Main Content Tabs: Questions vs Solutions -->
            <div class="content-tabs">
                <button class="content-tab active" data-section="questions">
                    📝 Questions
                </button>
                <button class="content-tab" data-section="solutions">
                    ✅ Solutions
                </button>
            </div>

            <!-- Search Section -->
            <div class="tabs">
                <button class="tab active" data-tab="text">📝 Text Search</button>
                <button class="tab" data-tab="image">📷 Image Search</button>
            </div>

            <!-- Text Search -->
            <div id="textTab" class="tab-content active">
                <div class="search-box">
                    <textarea id="searchInput" class="search-input" 
                              placeholder="Search questions or solutions..." 
                              rows="3"></textarea>
                    <button id="searchBtn" class="search-btn">🔍 Search</button>
                </div>
            </div>

            <!-- Image Search -->
            <div id="imageTab" class="tab-content">
                <div class="upload-box">
                    <div class="upload-area" id="uploadArea">
                        <div class="upload-icon">📷</div>
                        <h3>Upload Question/Diagram</h3>
                        <input type="file" id="imageInput" accept="image/*" hidden>
                        <button class="btn-primary" onclick="document.getElementById('imageInput').click()">
                            Choose Image
                        </button>
                    </div>
                    <div id="imagePreview" class="image-preview" style="display: none;">
                        <img id="previewImg" alt="Preview">
                        <div id="ocrText" class="ocr-text"></div>
                        <div class="btn-group">
                            <button id="clearBtn" class="btn-secondary">Clear</button>
                            <button id="searchImageBtn" class="btn-primary">Search</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Options -->
            <div class="options">
                <label>Results: 
                    <select id="topK">
                        <option value="10">10</option>
                        <option value="20">20</option>
                        <option value="50">50</option>
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
                <h2>Search Questions or Solutions</h2>
                <p>Use the tabs above to switch between questions and solutions</p>
            </div>
        </div>
    </main>

    <!-- Modal -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Details</h2>
                <button class="modal-close">&times;</button>
            </div>
            <div id="modalBody" class="modal-body"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <script src="app_enhanced.js"></script>
</body>
</html>
'''

# Enhanced JavaScript
enhanced_js = '''const API_URL = 'http://localhost:8000';

let currentSection = 'questions'; // 'questions' or 'solutions'

// Content tabs (Questions vs Solutions)
document.querySelectorAll('.content-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.content-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        currentSection = tab.dataset.section;
        document.getElementById('searchInput').placeholder = 
            `Search ${currentSection}...`;
        
        // Clear results
        document.getElementById('results').innerHTML = '';
        document.getElementById('emptyState').style.display = 'block';
        
        // Update stats
        loadStats();
    });
});

// Search tabs (Text vs Image)
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(tc => {
            tc.classList.remove('active');
        });
        document.getElementById(tab.dataset.tab + 'Tab').classList.add('active');
    });
});

// Search
document.getElementById('searchBtn').addEventListener('click', handleSearch);
document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSearch();
    }
});

// Image upload
document.getElementById('imageInput').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleImage(file);
});

document.getElementById('clearBtn').addEventListener('click', clearImage);
document.getElementById('searchImageBtn').addEventListener('click', () => {
    const text = document.getElementById('ocrText').textContent;
    if (text) performSearch(text);
});

// Modal
document.querySelector('.modal-close').addEventListener('click', () => {
    document.getElementById('modal').classList.remove('active');
});

async function loadStats() {
    try {
        const [questionsResp, solutionsResp] = await Promise.all([
            fetch(`${API_URL}/api/questions`),
            fetch(`${API_URL}/api/solutions`)
        ]);
        
        const questionsData = await questionsResp.json();
        const solutionsData = await solutionsResp.json();
        
        document.getElementById('totalQuestions').textContent = questionsData.total || 0;
        document.getElementById('totalSolutions').textContent = solutionsData.total || 0;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function handleSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return alert('Enter search query');
    
    performSearch(query);
}

async function performSearch(query) {
    showLoading('Searching...');
    document.getElementById('results').innerHTML = '';
    document.getElementById('emptyState').style.display = 'none';
    
    try {
        const endpoint = currentSection === 'questions' ? 
            '/api/search/questions' : '/api/search/solutions';
        
        const params = new URLSearchParams({
            query: query,
            top_k: document.getElementById('topK').value
        });
        
        const response = await fetch(`${API_URL}${endpoint}?${params}`);
        const data = await response.json();
        
        displayResults(data.results, query, currentSection);
    } catch (error) {
        console.error(error);
        document.getElementById('results').innerHTML = 
            '<div class="result-card"><p>⚠️ Error connecting to server</p></div>';
    } finally {
        hideLoading();
    }
}

function displayResults(results, query, section) {
    const resultsDiv = document.getElementById('results');
    
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="result-card">
                <p>No ${section} found for "${escapeHtml(query)}"</p>
            </div>
        `;
        return;
    }
    
    resultsDiv.innerHTML = `
        <h2>Found ${results.length} ${section}</h2>
    `;
    
    results.forEach((result, i) => {
        const card = createResultCard(result, i + 1, section);
        resultsDiv.appendChild(card);
    });
}

function createResultCard(result, num, section) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.onclick = () => showDetail(result, section);
    
    const score = result.combined_score || 0;
    const scoreClass = score >= 0.8 ? 'score-high' : score >= 0.6 ? 'score-medium' : 'score-low';
    
    const icon = section === 'questions' ? '❓' : '✅';
    
    card.innerHTML = `
        <div class="result-header">
            <div class="result-number">${icon} ${num}</div>
            <div class="result-score ${scoreClass}">${(score * 100).toFixed(0)}%</div>
        </div>
        <div class="result-question">${escapeHtml(result.question)}</div>
        <div class="result-meta">
            <span>📄 ${getFileName(result.file)}</span>
            <span>📖 Page ${result.location?.page || 'N/A'}</span>
            <span>🏷️ ${section}</span>
        </div>
    `;
    
    return card;
}

function showDetail(result, section) {
    document.getElementById('modalTitle').textContent = 
        section === 'questions' ? 'Question Details' : 'Solution Details';
    
    document.getElementById('modalBody').innerHTML = `
        <div class="detail-section">
            <div class="detail-label">${section === 'questions' ? 'Question' : 'Solution'}</div>
            <div class="detail-content">${escapeHtml(result.question)}</div>
        </div>
        <div class="detail-grid">
            <div class="detail-section">
                <div class="detail-label">Source</div>
                <div class="detail-content">${getFileName(result.file)}</div>
            </div>
            <div class="detail-section">
                <div class="detail-label">Page</div>
                <div class="detail-content">Page ${result.location?.page || 'N/A'}</div>
            </div>
        </div>
        <button class="btn-primary" onclick="copyToClipboard(\`${escapeHtml(result.question).replace(/`/g, '\\`')}\`)">
            📋 Copy
        </button>
    `;
    
    document.getElementById('modal').classList.add('active');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => alert('Copied!'));
}

async function handleImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('imagePreview').style.display = 'block';
        extractText(e.target.result);
    };
    reader.readAsDataURL(file);
}

async function extractText(imageData) {
    showLoading('Extracting text...');
    try {
        const worker = await Tesseract.createWorker('eng');
        const { data: { text } } = await worker.recognize(imageData);
        await worker.terminate();
        
        document.getElementById('ocrText').textContent = text.trim() || 'No text detected';
    } catch (error) {
        document.getElementById('ocrText').textContent = 'Error extracting text';
    } finally {
        hideLoading();
    }
}

function clearImage() {
    document.getElementById('imageInput').value = '';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('imagePreview').style.display = 'none';
}

function showLoading(text) {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getFileName(path) {
    return path.split('/').pop().split('\\\\').pop();
}

loadStats();
'''

# Add CSS for content tabs
css_addition = '''
.content-tabs {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    padding: 0.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.content-tab {
    flex: 1;
    padding: 1rem 2rem;
    background: #f3f4f6;
    border: 2px solid transparent;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.content-tab.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.content-tab:hover:not(.active) {
    background: #e5e7eb;
    border-color: #667eea;
}
'''

# ============================================================
# Write all files
# ============================================================

files = {
    'src/utils/pdf_extractor.py': enhanced_processor,
    'frontend/index.html': enhanced_frontend,
    'frontend/app_enhanced.js': enhanced_js,
}

for path, content in files.items():
    Path(path).write_text(content)
    print(f"✓ Created {path}")

# Append CSS
with open('frontend/style.css', 'a') as f:
    f.write('\n' + css_addition)
print("✓ Updated frontend/style.css")

# Print API endpoints to add
print("\n" + "="*60)
print("✓ Questions & Solutions System Created!")
print("="*60)
print("\nAdd these endpoints to src/api/app.py:")
print(api_enhancement)
print("\nThen:")
print("  1. Rebuild: python3 main.py --rebuild")
print("  2. Start API: python3 src/api/app.py")
print("  3. Open: frontend/index.html")
print("\nFeatures:")
print("  ✅ Separate Questions and Solutions tabs")
print("  ✅ Search in questions only")
print("  ✅ Search in solutions only")
print("  ✅ Auto-detection of solution sections")
print("  ✅ Visual distinction (❓ vs ✅)")
print("="*60 + "\n")

