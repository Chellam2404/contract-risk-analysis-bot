"""
Risk Scorer - Assess contract and clause-level risks
"""
from typing import Dict, List
import os
from groq import Groq

class RiskScorer:
    """Score risk levels for contracts and clauses"""
    
    # Risk thresholds
    HIGH_RISK_THRESHOLD = 70
    MEDIUM_RISK_THRESHOLD = 40
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=api_key) if api_key else None
        
        # Risk weights for clause types
        self.clause_weights = {
            'prohibition': 1.2,
            'obligation': 1.0,
            'condition': 0.8,
            'right': 0.6,
            'definition': 0.3,
            'general': 0.5
        }
    
    def score_contract(self, contract_type: str, clauses: List[Dict]) -> Dict:
        """
        Calculate composite risk score for entire contract
        
        Returns:
            Dict with composite_score, risk_level, and flags
        """
        clause_scores = []
        risk_flags = []
        
        # Score each clause
        for clause in clauses:
            risk_result = self.score_clause(clause['text'], contract_type)
            clause['risk_score'] = risk_result['score']
            clause['risk_level'] = risk_result['level']
            clause_scores.append(risk_result['score'])
            
            # Collect high-risk flags
            if risk_result['level'] == 'high':
                risk_flags.extend(risk_result['flags'])
        
        # Calculate weighted composite score
        if clause_scores:
            composite_score = sum(clause_scores) / len(clause_scores)
        else:
            composite_score = 0
        
        # Determine risk level
        if composite_score >= self.HIGH_RISK_THRESHOLD:
            risk_level = 'high'
        elif composite_score >= self.MEDIUM_RISK_THRESHOLD:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'composite_score': round(composite_score, 2),
            'risk_level': risk_level,
            'flags': risk_flags,
            'clause_count': len(clauses),
            'high_risk_clauses': sum(1 for c in clauses if c.get('risk_level') == 'high')
        }
    
    def score_clause(self, clause_text: str, contract_type: str) -> Dict:
        """
        Score risk for individual clause
        
        Returns:
            Dict with score (0-100), level (low/medium/high), and flags
        """
        clause_lower = clause_text.lower()
        score = 0
        flags = []
        
        # Pattern-based risk detection
        risk_patterns = self._get_risk_patterns()
        
        for pattern_name, pattern_info in risk_patterns.items():
            if any(keyword in clause_lower for keyword in pattern_info['keywords']):
                score += pattern_info['weight']
                if pattern_info['weight'] >= 25:  # High risk patterns
                    flags.append({
                        'type': pattern_name,
                        'description': pattern_info['description']
                    })
        
        # Cap score at 100
        score = min(score, 100)
        
        # Determine level
        if score >= self.HIGH_RISK_THRESHOLD:
            level = 'high'
        elif score >= self.MEDIUM_RISK_THRESHOLD:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'score': score,
            'level': level,
            'flags': flags
        }
    
    def score_clause_with_llm(self, clause_text: str, contract_type: str) -> Dict:
        """
        Use GPT-4 for detailed clause risk assessment
        """
        if not self.client:
            return self.score_clause(clause_text, contract_type)
        
        try:
            prompt = f"""Analyze this clause from a {contract_type} contract for an Indian SME.

Clause: {clause_text}

Assess:
1. Risk level (low/medium/high) and score (0-100)
2. Specific concerns for SMEs
3. Compliance with Indian Contract Act 1872

Respond in JSON format:
{{
  "risk_score": <0-100>,
  "risk_level": "<low/medium/high>",
  "concerns": ["concern1", "concern2"],
  "rationale": "Brief explanation"
}}"""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a legal risk analyst for Indian SMEs. Provide concise, actionable risk assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                'score': result.get('risk_score', 50),
                'level': result.get('risk_level', 'medium'),
                'flags': [{'type': 'llm_analysis', 'description': c} for c in result.get('concerns', [])],
                'rationale': result.get('rationale', '')
            }
            
        except Exception as e:
            print(f"LLM scoring failed: {e}")
            return self.score_clause(clause_text, contract_type)
    
    def _get_risk_patterns(self) -> Dict:
        """Define risk patterns with weights"""
        return {
            'unilateral_termination': {
                'keywords': ['may terminate', 'right to terminate', 'terminate at will', 'terminate without cause', 'sole discretion'],
                'weight': 30,
                'description': 'One-sided termination rights (may be void per Indian Contract Act if arbitrary)'
            },
            'uncapped_liability': {
                'keywords': ['unlimited liability', 'no limit', 'without limitation', 'liable for all', 'indemnify against all'],
                'weight': 35,
                'description': 'Unlimited liability exposure'
            },
            'auto_renewal_lock_in': {
                'keywords': ['automatically renew', 'auto-renewal', 'lock-in period', 'cannot terminate during'],
                'weight': 20,
                'description': 'Auto-renewal or Lock-in period (check if > 3 years)'
            },
            'penalty_high': {
                'keywords': ['penalty', 'liquidated damages', 'forfeit', 'pay as damages'],
                'weight': 25,
                'description': 'Penalty clause (Indian courts distinguish between reasonable compensation and penalty)'
            },
            'non_compete_excessive': {
                'keywords': ['non-compete', 'shall not compete', 'restrictive covenant', 'after termination'],
                'weight': 30,
                'description': 'Post-termination non-compete (Often void in India under Sec 27 unless reasonable)'
            },
            'ip_transfer': {
                'keywords': ['transfer of intellectual property', 'ip rights transfer', 'ownership of all work', 'work for hire'],
                'weight': 25,
                'description': 'Intellectual property transfer'
            },
            'foreign_jurisdiction': {
                'keywords': ['courts of singapore', 'courts of london', 'exclusive jurisdiction of', 'outside india'],
                'weight': 40,
                'description': 'Foreign Jurisdiction (High cost/risk for Indian SME)'
            },
            'arbitration_cost': {
                'keywords': ['arbitration in london', 'singapore international arbitration', 'icc rules'],
                'weight': 35,
                'description': 'High-cost International Arbitration'
            },
            'ambiguous_terms': {
                'keywords': ['reasonable', 'best efforts', 'as soon as possible', 'appropriate'],
                'weight': 10,
                'description': 'Ambiguous or vague terms'
            }
        }
