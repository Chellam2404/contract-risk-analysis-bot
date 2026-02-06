"""
Test Risk Scoring Logic
"""
import pytest
from backend.llm.risk_scorer import RiskScorer

def test_high_risk_detection():
    """Test detection of high-risk clauses"""
    scorer = RiskScorer()
    
    clause = """
    The Company may terminate this agreement at any time without cause
    and without notice. The Employee shall have unlimited liability
    for any damages.
    """
    
    result = scorer.score_clause(clause, 'employment')
    
    assert result['level'] == 'high'
    assert result['score'] >= 70
    assert len(result['flags']) > 0

def test_low_risk_detection():
    """Test detection of low-risk clauses"""
    scorer = RiskScorer()
    
    clause = """
    The parties agree to maintain confidentiality of proprietary information
    disclosed during the term of this agreement.
    """
    
    result = scorer.score_clause(clause, 'employment')
    
    assert result['level'] == 'low'
    assert result['score'] < 40

def test_composite_score():
    """Test composite contract risk scoring"""
    scorer = RiskScorer()
    
    clauses = [
        {'text': 'Standard payment terms apply.', 'type': 'obligation'},
        {'text': 'Party may terminate without cause.', 'type': 'prohibition'},
        {'text': 'Unlimited liability for all damages.', 'type': 'obligation'}
    ]
    
    result = scorer.score_contract('service', clauses)
    
    assert 'composite_score' in result
    assert 'risk_level' in result
    assert result['risk_level'] in ['low', 'medium', 'high']
    assert 0 <= result['composite_score'] <= 100
