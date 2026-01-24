// UI Components

class Components {
    createResultCard(result, index) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        const score = result.combined_score || 0;
        const scoreClass = score >= 0.8 ? 'high' : score >= 0.6 ? 'medium' : 'low';
        const scorePercent = (score * 100).toFixed(0);
        
        card.innerHTML = `
            <div class="result-header">
                <span class="result-number">${index}</span>
                <div class="result-score">
                    <span class="score-badge ${scoreClass}">${scorePercent}% Match</span>
                </div>
            </div>
            
            <div class="result-question">
                ${this.escapeHtml(result.question)}
            </div>
            
            <div class="result-meta">
                <div class="meta-item">
                    <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span>${this.getFileName(result.file)}</span>
                </div>
                
                ${result.location && result.location.page ? `
                <div class="meta-item">
                    <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span>Page ${result.location.page}</span>
                </div>
                ` : ''}
                
                ${result.question_type ? `
                <div class="meta-item">
                    <span class="type-badge">${result.question_type}</span>
                </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createQuestionDetailsHTML(result) {
        const score = result.combined_score || 0;
        const scorePercent = (score * 100).toFixed(1);
        
        return `
            <div style="margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">Question</h4>
                <p style="font-size: 1.125rem; line-height: 1.75; color: var(--text-primary);">
                    ${this.escapeHtml(result.question)}
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;">
                <div>
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase;">Source File</h4>
                    <p style="color: var(--text-primary);">${this.getFileName(result.file)}</p>
                </div>
                
                ${result.location && result.location.page ? `
                <div>
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase;">Page</h4>
                    <p style="color: var(--text-primary);">Page ${result.location.page}</p>
                </div>
                ` : ''}
                
                ${result.question_type ? `
                <div>
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase;">Question Type</h4>
                    <p style="color: var(--text-primary); text-transform: capitalize;">${result.question_type}</p>
                </div>
                ` : ''}
                
                <div>
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase;">Similarity Score</h4>
                    <p style="color: var(--text-primary);">${scorePercent}%</p>
                </div>
            </div>
            
            ${result.semantic_score ? `
            <div style="padding: 1rem; background: var(--bg-tertiary); border-radius: var(--border-radius); margin-bottom: 1rem;">
                <h4 style="margin-bottom: 0.75rem; color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase;">Score Breakdown</h4>
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span>Semantic Similarity:</span>
                        <span style="font-weight: 600;">${(result.semantic_score * 100).toFixed(1)}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>String Similarity:</span>
                        <span style="font-weight: 600;">${(result.string_score * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
            ` : ''}
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getFileName(path) {
        return path.split('/').pop().split('\\').pop();
    }
}