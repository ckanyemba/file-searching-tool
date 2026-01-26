const API_URL = 'http://localhost:8000';

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
        <button class="btn-primary" onclick="copyToClipboard(\`${escapeHtml(result.question).replace(/`/g, '\`')}\`)">
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
    return path.split('/').pop().split('\\').pop();
}

loadStats();
