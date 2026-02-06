"""
Explainer - Generate plain-language explanations
"""
from typing import Dict, List
import os
from groq import Groq

class Explainer:
    """Generate SME-friendly explanations of contract terms"""
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=api_key) if api_key else None
    
    def explain_contract(self, contract_type: str, clauses: List[Dict], risk_analysis: Dict) -> Dict:
        """
        Generate executive summary and recommendations for entire contract
        """
        if not self.client:
            return self._generate_fallback_summary(contract_type, clauses, risk_analysis)
        
        try:
            # Prepare high-risk clauses for focus
            high_risk_clauses = [c for c in clauses if c.get('risk_level') == 'high']
            
            prompt = f"""Summarize this {contract_type} contract for a small business owner in India.

Contract Overview:
- Total Clauses: {len(clauses)}
- Risk Score: {risk_analysis['composite_score']}/100 ({risk_analysis['risk_level']})
- High-Risk Clauses: {len(high_risk_clauses)}

High-Risk Areas:
{self._format_risk_flags(risk_analysis['flags'])}

Provide:
1. Executive summary (2-3 sentences)
2. Top 3 concerns for SME
3. Top 3 recommendations

Use simple business language, avoid legal jargon."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a legal advisor helping Indian SMEs understand contracts. Use simple, clear language."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )
            
            explanation = response.choices[0].message.content
            
            return {
                'summary': explanation,
                'recommendations': self._extract_recommendations(explanation)
            }
            
        except Exception as e:
            print(f"Contract explanation failed: {e}")
            return self._generate_fallback_summary(contract_type, clauses, risk_analysis)
    
    def generate_contract_template(self, contract_type: str, requirements: str = "") -> str:
        """
        Generate a standardized SME-friendly contract template
        """
        if not self.client:
            return "Error: LLM client not configured. Cannot generate template."
            
        try:
            prompt = f"""Create a standardized, SME-friendly {contract_type} contract template for India.
            
Requirements:
{requirements}

Structure:
1. Title & Parties
2. Definitions
3. Scope of Work / Obligations
4. Payment Terms
5. Term & Termination (Balanced)
6. Confidentiality
7. Governing Law (India) & Dispute Resolution
8. Signatures

Make it simple, balanced, and compliant with Indian Contract Act 1872. Use clear headings and [placeholders] for variable info."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a legal expert creating balanced contract templates for Indian SMEs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Template generation failed: {e}")
            return "Error generating template. Please try again."
            
    def explain_clause(self, clause_text: str, risk_info: Dict) -> Dict:
        """
        Generate plain-language explanation for a specific clause
        """
        if not self.client:
            return self._generate_fallback_clause_explanation(clause_text, risk_info)
        
        try:
            prompt = f"""Explain this contract clause to a small business owner:

Clause: {clause_text}

Risk Level: {risk_info.get('level', 'medium')}

Provide:
1. What it means in simple terms
2. Why it matters for SMEs
3. Potential concerns
4. Alternative wording suggestion (if concerning)

Keep it concise and practical."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a legal advisor simplifying contract terms for Indian SMEs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            explanation = response.choices[0].message.content
            
            return {
                'plain_language': explanation,
                'concerns': self._extract_concerns(explanation),
                'alternatives': self._extract_alternatives(explanation)
            }
            
        except Exception as e:
            print(f"Clause explanation failed: {e}")
            return self._generate_fallback_clause_explanation(clause_text, risk_info)
    
    def _format_risk_flags(self, flags: List[Dict]) -> str:
        """Format risk flags for prompt"""
        if not flags:
            return "No major risk flags detected"
        
        return "\n".join([f"- {flag['type']}: {flag['description']}" for flag in flags[:5]])
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from LLM response"""
        recommendations = []
        lines = text.split('\n')
        in_recommendations = False
        
        for line in lines:
            if 'recommendation' in line.lower():
                in_recommendations = True
            elif in_recommendations and line.strip():
                recommendations.append(line.strip('- ').strip())
        
        return recommendations[:3] if recommendations else [
            "Review high-risk clauses with legal counsel",
            "Negotiate unfavorable terms before signing",
            "Keep detailed records of all obligations"
        ]
    
    def _extract_concerns(self, text: str) -> List[str]:
        """Extract concerns from explanation"""
        concerns = []
        lines = text.split('\n')
        
        for line in lines:
            if 'concern' in line.lower() or 'risk' in line.lower():
                concerns.append(line.strip('- ').strip())
        
        return concerns[:3]
    
    def _extract_alternatives(self, text: str) -> List[str]:
        """Extract alternative clauses from explanation"""
        alternatives = []
        lines = text.split('\n')
        in_alternatives = False
        
        for line in lines:
            if 'alternative' in line.lower() or 'suggest' in line.lower():
                in_alternatives = True
            elif in_alternatives and line.strip():
                alternatives.append(line.strip('- ').strip())
        
        return alternatives[:2]
    
    def _generate_fallback_summary(self, contract_type: str, clauses: List[Dict], risk_analysis: Dict) -> Dict:
        """Generate basic summary without LLM"""
        high_risk_count = risk_analysis.get('high_risk_clauses', 0)
        
        summary = f"""This {contract_type} contract contains {len(clauses)} clauses with an overall risk score of {risk_analysis['composite_score']}/100 ({risk_analysis['risk_level']} risk).

{high_risk_count} clause(s) require careful attention. Review all high-risk clauses with legal counsel before signing."""
        
        recommendations = [
            f"Review {high_risk_count} high-risk clause(s) carefully",
            "Consult legal advisor for unfavorable terms",
            "Document all obligations and deadlines"
        ]
        
        return {
            'summary': summary,
            'recommendations': recommendations
        }
    
    def _generate_fallback_clause_explanation(self, clause_text: str, risk_info: Dict) -> Dict:
        """Generate basic clause explanation without LLM"""
        return {
            'plain_language': f"This clause is classified as {risk_info.get('level', 'medium')} risk. Review carefully and consider legal consultation.",
            'concerns': ["Requires legal review", "May have unfavorable terms"],
            'alternatives': ["Negotiate more balanced terms"]
        }
