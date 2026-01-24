const API_URL = 'http://localhost:8000';

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
            <button class="btn-primary" onclick="copyToClipboard('${escapeHtml(result.question).replace(/'/g, "\'")}')">
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
    return path.split('/').pop().split('\\').pop();
}

// Load stats
fetch(`${API_URL}/api/stats`)
    .then(r => r.json())
    .then(data => {
        document.getElementById('totalQuestions').textContent = data.total_questions || 0;
        document.getElementById('totalFiles').textContent = Object.keys(data.questions_by_file || {}).length;
    })
    .catch(() => {});
