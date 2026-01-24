"""
API Endpoints
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')
search_system = None


def init_endpoints(system):
    """Initialize endpoints"""
    global search_system
    search_system = system


@api_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search endpoint"""
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
    else:
        query = request.args.get('query', '')
        top_k = int(request.args.get('top_k', 5))
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        if search_system:
            results = search_system.search_question(query=query, top_k=top_k)
        else:
            results = []
        return jsonify({'query': query, 'results': results, 'total': len(results)})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
def stats():
    """Stats endpoint"""
    try:
        if search_system:
            data = search_system.generate_statistics()
        else:
            data = {'total_questions': 0}
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})
