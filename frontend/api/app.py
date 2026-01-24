"""
Flask API for question search system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import QuestionSearchSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize search system
search_system = QuestionSearchSystem()
search_system.load_search_index()


@app.route('/api/search', methods=['GET'])
def search():
    """Search for questions"""
    query = request.args.get('query', '')
    search_type = request.args.get('search_type', 'semantic')
    top_k = int(request.args.get('top_k', 5))
    question_type = request.args.get('question_type')
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        results = search_system.search_question(
            query=query,
            top_k=top_k,
            search_type=search_type
        )
        
        # Filter by question type if specified
        if question_type and question_type != 'all':
            results = [
                r for r in results 
                if r.get('question_type') == question_type
            ]
        
        return jsonify({
            'query': query,
            'results': results,
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    try:
        stats = search_system.generate_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)