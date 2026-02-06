"""
Clause Similarity - Compare clauses against standard templates
"""
import spacy
import numpy as np
from typing import List, Dict, Tuple

class ClauseSimilarity:
    """Compare clauses using semantic similarity"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            self.nlp = None
            print("Warning: en_core_web_lg not found. Similarity matching will be disabled.")
    
    def compare_to_standard(self, clause_text: str, standard_clauses: List[str]) -> Dict:
        """
        Compare a clause against a list of standard clauses to find best match and deviation.
        
        Returns:
            Dict with 'match_score' (0-1), 'best_match_text', 'is_deviant'
        """
        if not self.nlp or not clause_text.strip():
            return {'match_score': 0, 'best_match_text': '', 'is_deviant': False}
            
        doc1 = self.nlp(clause_text)
        
        best_score = 0
        best_match = ""
        
        for std in standard_clauses:
            doc2 = self.nlp(std)
            score = doc1.similarity(doc2)
            if score > best_score:
                best_score = score
                best_match = std
        
        # If score is high (e.g. > 0.85), it's standard.
        # If score is medium (e.g. 0.6 - 0.85), it might be a deviation.
        # If score is low, it's a completely different clause.
        
        return {
            'match_score': float(best_score),
            'best_match_text': best_match,
            'is_deviant': 0.6 <= best_score < 0.9  # Flag if it looks similar but not quite right
        }
