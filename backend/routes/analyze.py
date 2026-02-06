"""
Analyze route - Process contracts and generate risk assessments
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from nlp.extractors.entity_extractor import EntityExtractor
from nlp.extractors.clause_extractor import ClauseExtractor
from nlp.classifiers.contract_classifier import ContractClassifier
from nlp.similarity import ClauseSimilarity  # [NEW]
from llm.risk_scorer import RiskScorer
from llm.explainer import Explainer
from utils.audit_logger import log_action
import json
import os

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/', methods=['POST'])
def analyze_contract():
    """
    Analyze a contract and return risk assessment
    Expected input: contract_id, text
    """
    try:
        data = request.get_json()
        
        if not data or 'contract_id' not in data or 'text' not in data:
            return jsonify({'error': 'Missing contract_id or text'}), 400
        
        contract_id = data['contract_id']
        text = data['text']
        
        # Step 1: Classify contract type
        classifier = ContractClassifier()
        contract_type = classifier.classify(text)
        
        # Step 2: Extract clauses
        clause_extractor = ClauseExtractor()
        clauses = clause_extractor.extract(text)
        
        # Step 3: Extract entities from each clause
        entity_extractor = EntityExtractor()
        
        # [NEW] Load standard template for comparison
        similarity_checker = ClauseSimilarity()
        standard_clauses = []
        try:
            template_path = f"data/templates/{contract_type}_template.json"
            # Fallback to general employment if specific not found, just for demo
            if not os.path.exists(template_path):
                 template_path = "data/templates/employment_template.json"
            
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                    standard_clauses = template_data.get('clauses', [])
        except Exception as e:
            print(f"Error loading template: {e}")

        for clause in clauses:
            clause['entities'] = entity_extractor.extract(clause['text'])
            
            # [NEW] Check similarity
            if standard_clauses:
                sim_result = similarity_checker.compare_to_standard(clause['text'], standard_clauses)
                clause['similarity_score'] = sim_result['match_score']
                clause['is_standard'] = sim_result['match_score'] > 0.9
                clause['deviation_flag'] = sim_result['is_deviant']
                if sim_result['is_deviant']:
                    clause['suggested_standard'] = sim_result['best_match_text']
        
        # Step 4: Risk scoring
        risk_scorer = RiskScorer()
        risk_analysis = risk_scorer.score_contract(contract_type, clauses)
        
        # Step 5: Generate plain-language explanations
        explainer = Explainer()
        explanations = explainer.explain_contract(contract_type, clauses, risk_analysis)
        
        # Combine results
        result = {
            'contract_id': contract_id,
            'contract_type': contract_type,
            'risk_score': risk_analysis['composite_score'],
            'risk_level': risk_analysis['risk_level'],
            'clauses': clauses,
            'risk_flags': risk_analysis['flags'],
            'summary': explanations['summary'],
            'recommendations': explanations['recommendations'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Log action
        log_action(contract_id, 'analyze', {
            'contract_type': contract_type,
            'risk_score': risk_analysis['composite_score'],
            'clause_count': len(clauses)
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'details': str(e)
        }), 500

@analyze_bp.route('/clause/<clause_id>', methods=['POST'])
def analyze_clause(clause_id):
    """
    Analyze a specific clause in detail
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing clause text'}), 400
        
        clause_text = data['text']
        contract_type = data.get('contract_type', 'general')
        
        # Extract entities
        entity_extractor = EntityExtractor()
        entities = entity_extractor.extract(clause_text)
        
        # Risk scoring for single clause
        risk_scorer = RiskScorer()
        clause_risk = risk_scorer.score_clause(clause_text, contract_type)
        
        # Generate explanation
        explainer = Explainer()
        explanation = explainer.explain_clause(clause_text, clause_risk)
        
        return jsonify({
            'clause_id': clause_id,
            'entities': entities,
            'risk_level': clause_risk['level'],
            'risk_score': clause_risk['score'],
            'explanation': explanation['plain_language'],
            'concerns': explanation['concerns'],
            'alternatives': explanation['alternatives'],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Clause analysis failed',
            'details': str(e)
        }), 500
