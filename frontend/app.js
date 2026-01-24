// Main Application Logic

class QuestionSearchApp {
    constructor() {
        this.api = new QuestionAPI();
        this.components = new Components();
        this.currentResults = [];
        
        this.init();
    }

    init() {
        this.bindElements();
        this.attachEventListeners();
        this.loadStats();
    }

    bindElements() {
        // Search elements
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.clearBtn = document.getElementById('clearBtn');
        
        // Options
        this.searchTypeRadios = document.querySelectorAll('input[name="searchType"]');
        this.questionTypeFilter = document.getElementById('questionTypeFilter');
        this.topKSelect = document.getElementById('topKSelect');
        
        // Results
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.resultsTitle = document.getElementById('resultsTitle');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.emptyState = document.getElementById('emptyState');
        
        // Actions
        this.exportBtn = document.getElementById('exportBtn');
        
        // Stats
        this.totalQuestions = document.getElementById('totalQuestions');
        this.totalExams = document.getElementById('totalExams');
        
        // Modal
        this.modal = document.getElementById('questionModal');
        this.modalBody = document.getElementById('modalBody');
    }

    attachEventListeners() {
        // Search
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        
        // Clear button
        this.searchInput.addEventListener('input', (e) => {
            this.clearBtn.style.display = e.target.value ? 'block' : 'none';
        });
        this.clearBtn.addEventListener('click', () => this.clearSearch());
        
        // Example queries
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.dataset.query;
                this.searchInput.value = query;
                this.handleSearch();
            });
        });
        
        // Export
        this.exportBtn.addEventListener('click', () => this.exportResults());
        
        // Modal close
        this.modal.querySelector('.modal-close').addEventListener('click', () => {
            this.modal.classList.remove('active');
        });
        
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.classList.remove('active');
            }
        });
    }

    async loadStats() {
        try {
            const stats = await this.api.getStats();
            this.totalQuestions.textContent = stats.total_questions || 0;
            this.totalExams.textContent = Object.keys(stats.questions_by_file || {}).length;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async handleSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        const searchType = document.querySelector('input[name="searchType"]:checked').value;
        const topK = parseInt(this.topKSelect.value);
        const questionType = this.questionTypeFilter.value;

        this.showLoading();

        try {
            const results = await this.api.search(query, {
                searchType,
                topK,
                questionType: questionType !== 'all' ? questionType : null
            });

            this.currentResults = results;
            this.displayResults(results, query);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayResults(results, query) {
        this.emptyState.style.display = 'none';
        this.resultsSection.style.display = 'block';

        this.resultsTitle.textContent = `Found ${results.length} results for "${query}"`;
        
        this.resultsContainer.innerHTML = '';

        if (results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="empty-state">
                    <p>No matching questions found. Try a different search term.</p>
                </div>
            `;
            return;
        }

        results.forEach((result, index) => {
            const card = this.components.createResultCard(result, index + 1);
            card.addEventListener('click', () => this.showQuestionDetails(result));
            this.resultsContainer.appendChild(card);
        });
    }

    showQuestionDetails(result) {
        this.modalBody.innerHTML = this.components.createQuestionDetailsHTML(result);
        this.modal.classList.add('active');
    }

    clearSearch() {
        this.searchInput.value = '';
        this.clearBtn.style.display = 'none';
        this.searchInput.focus();
    }

    showLoading() {
        this.loadingIndicator.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.emptyState.style.display = 'none';
    }

    hideLoading() {
        this.loadingIndicator.style.display = 'none';
    }

    showError(message) {
        alert(message); // Replace with better error handling
    }

    exportResults() {
        if (this.currentResults.length === 0) {
            this.showError('No results to export');
            return;
        }

        const data = this.currentResults.map((r, i) => ({
            rank: i + 1,
            question: r.question,
            file: r.file,
            score: r.combined_score,
            type: r.question_type || 'N/A'
        }));

        const csv = this.convertToCSV(data);
        this.downloadFile(csv, 'search_results.csv', 'text/csv');
    }

    convertToCSV(data) {
        const headers = Object.keys(data[0]);
        const csv = [
            headers.join(','),
            ...data.map(row => headers.map(header => 
                `"${String(row[header]).replace(/"/g, '""')}"`
            ).join(','))
        ].join('\n');
        return csv;
    }

    downloadFile(content, filename, type) {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new QuestionSearchApp();
});