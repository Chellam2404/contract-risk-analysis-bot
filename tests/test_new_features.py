import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.nlp.extractors.clause_extractor import ClauseExtractor
from backend.nlp.similarity import ClauseSimilarity

class TestNewFeatures(unittest.TestCase):
    def test_hindi_clause_extraction(self):
        extractor = ClauseExtractor()
        # Test Hindi text
        hindi_text = "ग्राहक को 30 दिनों के भीतर भुगतान करना होगा।" # "Customer must pay within 30 days"
        self.assertEqual(extractor._classify_clause(hindi_text), 'obligation')
        
        hindi_right = "कर्मचारी को छुट्टी का अधिकार है।" # "Employee has right to leave"
        self.assertEqual(extractor._classify_clause(hindi_right), 'right')
        
    def test_clause_similarity(self):
        sim = ClauseSimilarity()
        if not sim.nlp:
            print("Skipping similarity test - spacy model not loaded")
            return
            
        std_clause = "The Employee agrees not to disclose any Confidential Information."
        similar_clause = "The Worker shall not reveal any Secret Data."
        different_clause = "The weather is nice today."
        
        result_sim = sim.compare_to_standard(similar_clause, [std_clause])
        result_diff = sim.compare_to_standard(different_clause, [std_clause])
        
        print(f"Similarity Score: {result_sim['match_score']}")
        print(f"Different Score: {result_diff['match_score']}")
        
        self.assertTrue(result_sim['match_score'] > result_diff['match_score'])

if __name__ == '__main__':
    unittest.main()
