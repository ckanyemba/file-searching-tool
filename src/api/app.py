"""
Flask API for Question Search System
Run this file to start the REST API server
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from main import QuestionSearchSystem
from src.api.endpoints import api_bp, init_endpoints

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(database_path='database'):
    """Create and configure the Flask application"""
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize search system
    logger.info("Initializing Question Search System...")
    search_system = QuestionSearchSystem(database_path=database_path)
    
    # Try to load existing index
    if not search_system.load_search_index():
        logger.warning("Search index not found. Building new index...")
        try:
            search_system.extract_all_questions()
            search_system.build_search_index()
            logger.info("Index built successfully")
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            logger.info("API will start but search may not work properly")
    else:
        logger.info("Search index loaded successfully")
    
    # Initialize endpoints with search system
    init_endpoints(search_system)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'COS3701 Question Search API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'search': '/api/search',
                'stats': '/api/stats',
                'debug': '/api/debug/search',
                'questions': '/api/questions',
                'solutions': '/api/solutions',
                'search_questions': '/api/search/questions',
                'search_solutions': '/api/search/solutions',
                'search_diagram': '/api/search/diagram',
                'files': '/api/files',
                'health': '/api/health'
            }
        })
    
    # Additional routes (inside create_app)
    @app.route('/api/search/diagram', methods=['POST'])
    def search_by_diagram():
        """Search using uploaded diagram image"""
        if 'diagram' not in request.files:
            return jsonify({'error': 'No diagram provided'}), 400
        
        file = request.files['diagram']
        
        try:
            from src.core.diagram_similarity import DiagramSearchEngine
            import tempfile
            
            # Save uploaded diagram
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name
            
            # Search for similar diagrams
            engine = DiagramSearchEngine()
            results = engine.search_with_diagram(
                tmp_path,
                search_system.all_questions,
                top_k=10
            )
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            return jsonify({
                'results': results,
                'total': len(results)
            })
        
        except Exception as e:
            logger.error(f"Diagram search error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/questions', methods=['GET'])
    def get_questions_only():
        """Get only questions"""
        try:
            if not search_system or not search_system.all_questions:
                return jsonify({'questions': [], 'total': 0})
            
            questions = [q for q in search_system.all_questions if q.get('section') == 'questions']
            return jsonify({'questions': questions, 'total': len(questions)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/solutions', methods=['GET'])
    def get_solutions_only():
        """Get only solutions"""
        try:
            if not search_system or not search_system.all_questions:
                return jsonify({'solutions': [], 'total': 0})
            
            solutions = [q for q in search_system.all_questions if q.get('section') == 'solutions']
            return jsonify({'solutions': solutions, 'total': len(solutions)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/search/questions', methods=['GET'])
    def search_questions_only():
        """Search only questions"""
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'Query required'}), 400
        
        try:
            questions_only = [q for q in search_system.all_questions if q.get('section') == 'questions']
            temp_engine = search_system.search_engine
            temp_engine.questions = questions_only
            results = temp_engine.search(query, top_k=10)
            return jsonify({'query': query, 'results': results, 'total': len(results)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/debug/search', methods=['GET'])
    def debug_search():
        """Debug search endpoint"""
        query = request.args.get('query', '')
        if not query:
         return jsonify({'error': 'Query required'}), 400
    
        try:
            # Direct search without filtering
            results = search_system.search(query, top_k=10)
        
            return jsonify({
            'query': query,
            'total_questions': len(search_system.all_questions),
            'results_found': len(results),
            'results': results
            })
        except Exception as e:
            logger.error(f"Debug search error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/search/solutions', methods=['GET'])
    def search_solutions_only():
        """Search only solutions"""
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'Query required'}), 400
        
        try:
            solutions_only = [q for q in search_system.all_questions if q.get('section') == 'solutions']
            temp_engine = search_system.search_engine
            temp_engine.questions = solutions_only
            results = temp_engine.search(query, top_k=10)
            return jsonify({'query': query, 'results': results, 'total': len(results)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='COS3701 Question Search API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--database', default='database', help='Database path')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create app
    app = create_app(database_path=args.database)
    
    # Print startup info
    print("\n" + "="*60)
    print("COS3701 Question Search API Server")
    print("="*60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Database: {args.database}")
    print(f"Debug: {args.debug}")
    print("\nAPI Endpoints:")
    print(f"  - http://{args.host}:{args.port}/")
    print(f"  - http://{args.host}:{args.port}/api/search")
    print(f"  - http://{args.host}:{args.port}/api/stats")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Run app
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()