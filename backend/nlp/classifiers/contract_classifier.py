"""
Contract Classifier - Identify contract type
"""
from typing import Dict

class ContractClassifier:
    """Classify contract into predefined types"""
    
    def __init__(self):
        # Keywords for each contract type
        self.type_keywords = {
            'employment': [
                'employment', 'employee', 'employer', 'salary', 'wages',
                'job title', 'position', 'employment agreement', 'work hours',
                'leave', 'resignation', 'termination of employment'
            ],
            'vendor': [
                'vendor', 'supplier', 'purchase', 'procurement', 'delivery',
                'goods', 'services', 'purchase order', 'vendor agreement',
                'supply', 'shipment'
            ],
            'lease': [
                'lease', 'rent', 'tenant', 'landlord', 'premises', 'property',
                'rental', 'lease agreement', 'lease term', 'security deposit',
                'maintenance', 'lease renewal'
            ],
            'partnership': [
                'partnership', 'partners', 'profit sharing', 'capital contribution',
                'partnership agreement', 'joint venture', 'partnership deed',
                'profit and loss', 'partnership business'
            ],
            'service': [
                'service agreement', 'professional services', 'consulting',
                'contractor', 'independent contractor', 'scope of work',
                'deliverables', 'service provider', 'client', 'project'
            ]
        }
    
    def classify(self, text: str) -> str:
        """
        Classify contract based on keyword matching
        
        Returns:
            Contract type: employment, vendor, lease, partnership, service, or general
        """
        text_lower = text.lower()
        
        scores = {}
        
        # Score each contract type
        for contract_type, keywords in self.type_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences
                count = text_lower.count(keyword)
                score += count
            scores[contract_type] = score
        
        # Get highest scoring type
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def get_confidence(self, text: str) -> Dict[str, float]:
        """
        Get classification confidence scores for all types
        
        Returns:
            Dict with contract types and normalized confidence scores
        """
        text_lower = text.lower()
        scores = {}
        
        for contract_type, keywords in self.type_keywords.items():
            score = 0
            for keyword in keywords:
                count = text_lower.count(keyword)
                score += count
            scores[contract_type] = score
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores
