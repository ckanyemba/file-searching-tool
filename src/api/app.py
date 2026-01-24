"""
========================
CORRECTED API FILES
========================
"""

# ========================================
# src/api/app.py (CORRECTED)
# ========================================

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
                'questions': '/api/questions',
                'files': '/api/files',
                'health': '/api/health'
            }
        })
    
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
