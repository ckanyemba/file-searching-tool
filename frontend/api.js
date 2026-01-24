// API Communication Layer

class QuestionAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    async search(query, options = {}) {
        const {
            searchType = 'semantic',
            topK = 5,
            questionType = null
        } = options;

        const params = new URLSearchParams({
            query,
            search_type: searchType,
            top_k: topK.toString()
        });

        if (questionType) {
            params.append('question_type', questionType);
        }

        try {
            const response = await fetch(`${this.baseURL}/api/search?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.results || [];
        } catch (error) {
            console.error('API Error:', error);
            
            // Return mock data for development
            return this.getMockResults(query);
        }
    }

    async getStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/stats`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            
            // Return mock stats for development
            return {
                total_questions: 250,
                questions_by_file: {
                    'COS3701_OctNov_2025.pdf': 85,
                    'COS3701_MayJune_2024.pdf': 90,
                    'COS3701_OctNov_2023.pdf': 75
                }
            };
        }
    }

    // Mock data for development/testing
    getMockResults(query) {
        return [
            {
                question: 'Prove that the language PALINDROME is non-context-free.',
                file: 'database/exam_papers/COS3701_MayJune_2024.pdf',
                location: { page: 5 },
                semantic_score: 0.92,
                string_score: 0.87,
                combined_score: 0.90,
                question_type: 'proof'
            },
            {
                question: 'Show that PALINDROME is not a context-free language using the pumping lemma.',
                file: 'database/exam_papers/COS3701_OctNov_2023.pdf',
                location: { page: 8 },
                semantic_score: 0.88,
                string_score: 0.82,
                combined_score: 0.86,
                question_type: 'proof'
            },
            {
                question: 'Build a TM that accepts the language {a^n b^n}.',
                file: 'database/exam_papers/COS3701_OctNov_2025.pdf',
                location: { page: 12 },
                semantic_score: 0.75,
                string_score: 0.68,
                combined_score: 0.72,
                question_type: 'build'
            },
            {
                question: 'Is PALINDROME a regular language? Justify your answer.',
                file: 'database/exam_papers/COS3701_MayJune_2024.pdf',
                location: { page: 3 },
                semantic_score: 0.70,
                string_score: 0.65,
                combined_score: 0.68,
                question_type: 'explain'
            },
            {
                question: 'Draw a PDA that accepts PALINDROME.',
                file: 'database/exam_papers/COS3701_OctNov_2023.pdf',
                location: { page: 15 },
                semantic_score: 0.65,
                string_score: 0.60,
                combined_score: 0.63,
                question_type: 'draw'
            }
        ];
    }
}