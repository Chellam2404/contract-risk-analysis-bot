"""
Test Entity Extraction
"""
import pytest
from backend.nlp.extractors.entity_extractor import EntityExtractor

def test_party_extraction():
    """Test extraction of parties from contract text"""
    extractor = EntityExtractor()
    
    text = """
    This agreement is between ABC Corporation (the "Employer") 
    and John Smith (the "Employee").
    """
    
    entities = extractor.extract(text)
    
    # Check that parties are extracted
    assert len(entities['parties']) > 0
    party_texts = [p['text'] for p in entities['parties']]
    assert any('ABC Corporation' in pt or 'John Smith' in pt for pt in party_texts)

def test_amount_extraction():
    """Test extraction of monetary amounts"""
    extractor = EntityExtractor()
    
    text = """
    The monthly salary shall be Rs. 50,000 with an annual bonus 
    of up to Rs. 100,000.
    """
    
    entities = extractor.extract(text)
    
    # Check that amounts are extracted
    assert len(entities['amounts']) > 0

def test_duration_extraction():
    """Test extraction of time durations"""
    extractor = EntityExtractor()
    
    text = """
    The employee shall provide 30 days notice before resignation.
    The lock-in period is 2 years.
    """
    
    entities = extractor.extract(text)
    
    # Check that durations are extracted
    assert len(entities['durations']) >= 2
    durations = {d['text'].lower() for d in entities['durations']}
    assert any('30 day' in d for d in durations)
    assert any('2 year' in d for d in durations)

def test_jurisdiction_extraction():
    """Test extraction of jurisdiction clauses"""
    extractor = EntityExtractor()
    
    text = """
    This agreement shall be governed by the laws of India.
    Any disputes shall be subject to the jurisdiction of courts in Mumbai.
    """
    
    entities = extractor.extract(text)
    
    # Check that jurisdiction is extracted
    assert len(entities['jurisdiction']) > 0
