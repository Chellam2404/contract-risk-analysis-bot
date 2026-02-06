"""
Test Contract Classification
"""
import pytest
from backend.nlp.classifiers.contract_classifier import ContractClassifier

def test_employment_classification():
    """Test classification of employment contract"""
    classifier = ContractClassifier()
    
    text = """
    Employment Agreement
    This agreement is between XYZ Company (Employer) and Jane Doe (Employee).
    Position: Software Engineer
    Salary: Rs. 80,000 per month
    Leave: 21 days paid leave per year
    """
    
    contract_type = classifier.classify(text)
    assert contract_type == 'employment'

def test_vendor_classification():
    """Test classification of vendor contract"""
    classifier = ContractClassifier()
    
    text = """
    Vendor Agreement
    This purchase order is for the supply of 100 units of Product X
    to be delivered by the vendor within 30 days.
    Payment terms: Net 30 days after delivery.
    """
    
    contract_type = classifier.classify(text)
    assert contract_type == 'vendor'

def test_lease_classification():
    """Test classification of lease agreement"""
    classifier = ContractClassifier()
    
    text = """
    Lease Agreement
    The landlord agrees to lease the premises located at 123 Main Street
    to the tenant for a monthly rent of Rs. 25,000.
    Security deposit: Rs. 50,000
    Lease term: 11 months
    """
    
    contract_type = classifier.classify(text)
    assert contract_type == 'lease'

def test_service_classification():
    """Test classification of service contract"""
    classifier = ContractClassifier()
    
    text = """
    Professional Services Agreement
    The consultant agrees to provide software development services
    to the client. Scope of work includes design, development, and testing.
    Deliverables shall be submitted within 3 months.
    """
    
    contract_type = classifier.classify(text)
    assert contract_type == 'service'
