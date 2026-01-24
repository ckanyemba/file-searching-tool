# ========================================
# 5. src/api/endpoints.py
# ========================================

"""
API Endpoints
"""

from flask import Blueprint, request, jsonify
from typing import Optional
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Global search system instance (set by app.py)
search_system = None


def init_endpoints(system):
    """Initialize endpoints with search system"""
    global search_system
    search_system = system


@api_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search for questions"""
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('search_type', 'semantic')
        top_k = data.get('top_k', 5)
        question_type = data.get('question_type')
    else:
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
            'search_type': search_type,
            'results': results,
            'total': len(results)
        })
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    try:
        stats = search_system.generate_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/questions', methods=['GET'])
def list_questions():
    """List all questions with pagination"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    try:
        all_questions = search_system.all_questions
        total = len(all_questions)
        
        start = (page - 1) * per_page
        end = start + per_page
        
        questions = all_questions[start:end]
        
        return jsonify({
            'questions': questions,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    
    except Exception as e:
        logger.error(f"List questions error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/files', methods=['GET'])
def list_files():
    """List all exam files"""
    try:
        stats = search_system.generate_statistics()
        files = stats.get('questions_by_file', {})
        
        file_list = [
            {
                'filename': filename,
                'question_count': count
            }
            for filename, count in files.items()
        ]
        
        return jsonify({
            'files': file_list,
            'total': len(file_list)
        })
    
    except Exception as e:
        logger.error(f"List files error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })


@api_bp.route('/rebuild', methods=['POST'])
def rebuild_index():
    """Rebuild search index (admin endpoint)"""
    try:
        search_system.extract_all_questions(force_reextract=True)
        search_system.build_search_index()
        
        return jsonify({
            'status': 'success',
            'message': 'Index rebuilt successfully'
        })
    
    except Exception as e:
        logger.error(f"Rebuild error: {e}")
        return jsonify({'error': str(e)}), 500
