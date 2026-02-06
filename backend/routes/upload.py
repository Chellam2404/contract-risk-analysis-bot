"""
Upload route - Handle contract file uploads
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

from nlp.parsers.document_parser import DocumentParser
from utils.audit_logger import log_action

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['POST'])
def upload_contract():
    """
    Upload and parse a contract document
    Returns: contract_id, extracted_text, file_info
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Generate unique contract ID
        contract_id = str(uuid.uuid4())
        
        # Secure the filename
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Save file with contract ID
        upload_folder = 'data/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, f"{contract_id}.{file_extension}")
        file.save(filepath)
        
        # Parse document
        parser = DocumentParser()
        parsed_data = parser.parse(filepath, file_extension)
        
        if not parsed_data['success']:
            return jsonify({
                'error': 'Failed to parse document',
                'details': parsed_data.get('error', 'Unknown error')
            }), 400
        
        # Log action
        log_action(contract_id, 'upload', {
            'filename': filename,
            'file_type': file_extension,
            'text_length': len(parsed_data['text'])
        })
        
        return jsonify({
            'success': True,
            'contract_id': contract_id,
            'filename': filename,
            'file_type': file_extension,
            'text_length': len(parsed_data['text']),
            'text': parsed_data['text'],
            'text_preview': parsed_data['text'][:500],  # First 500 chars
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Upload failed',
            'details': str(e)
        }), 500
