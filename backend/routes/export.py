"""
Export route - Generate PDF reports
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os

from utils.pdf_generator import generate_report
from utils.audit_logger import log_action
from llm.explainer import Explainer

export_bp = Blueprint('export', __name__)

@export_bp.route('/template', methods=['POST'])
def generate_template():
    """
    Generate a standardized contract template
    """
    try:
        data = request.get_json()
        contract_type = data.get('contract_type', 'General Service')
        requirements = data.get('requirements', '')
        
        explainer = Explainer()
        template_text = explainer.generate_contract_template(contract_type, requirements)
        
        return jsonify({
            'success': True,
            'contract_type': contract_type,
            'template': template_text
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Template generation failed',
            'details': str(e)
        }), 500

@export_bp.route('/pdf', methods=['POST'])
def export_pdf():
    """
    Generate PDF report from analysis results
    """
    try:
        data = request.get_json()
        
        if not data or 'contract_id' not in data:
            return jsonify({'error': 'Missing contract_id'}), 400
        
        contract_id = data['contract_id']
        analysis_data = data.get('analysis', {})
        
        # Generate PDF
        pdf_path = generate_report(contract_id, analysis_data)
        
        # Log action
        log_action(contract_id, 'export_pdf', {
            'filename': os.path.basename(pdf_path)
        })
        
        # Send file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'contract_analysis_{contract_id}.pdf'
        )
        
    except Exception as e:
        return jsonify({
            'error': 'PDF export failed',
            'details': str(e)
        }), 500

@export_bp.route('/json', methods=['POST'])
def export_json():
    """
    Export analysis as JSON for legal review
    """
    try:
        data = request.get_json()
        
        if not data or 'contract_id' not in data:
            return jsonify({'error': 'Missing contract_id'}), 400
        
        contract_id = data['contract_id']
        
        # Log action
        log_action(contract_id, 'export_json', {})
        
        # Return formatted JSON
        return jsonify({
            'success': True,
            'contract_id': contract_id,
            'analysis': data.get('analysis', {}),
            'exported_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'JSON export failed',
            'details': str(e)
        }), 500
