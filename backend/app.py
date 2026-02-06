"""
Legal Contract Assistant - Main Flask Application
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

# Import routes
from routes.analyze import analyze_bp
from routes.upload import upload_bp
from routes.export import export_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
# Serving frontend from ../frontend
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend requests

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Register blueprints
app.register_blueprint(analyze_bp, url_prefix='/api/analyze')
app.register_blueprint(upload_bp, url_prefix='/api/upload')
app.register_blueprint(export_bp, url_prefix='/api/export')

@app.route('/')
def index():
    """Serve the frontend"""
    return app.send_static_file('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Legal Contract Assistant API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error occurred.'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data/uploads', exist_ok=True)
    os.makedirs('data/audit_logs', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
