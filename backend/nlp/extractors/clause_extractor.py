"""
Clause Extractor - Segment contract into clauses
"""
import re
from typing import List, Dict

class ClauseExtractor:
    """Extract and classify clauses from contract text"""
    
    def __init__(self):
        # Clause headers pattern (numbered sections) - Supports "1. Title", "1.1 Title", "ARTICLE 1"
        self.clause_header_pattern = r'(?i)\n(\d+(\.\d+)*\.?\s+[a-z][a-z0-9\s\(\)\-\,]+|article\s+\d+)\n'
        
        # Obligation/Right/Prohibition keywords (English + Hindi)
        self.obligation_keywords = [
            'shall', 'must', 'required to', 'obligated to', 'agrees to',
            'करना होगा', 'बाध्य है', 'अनिवार्य', 'जिम्मेदारी'
        ]
        self.right_keywords = [
            'may', 'entitled to', 'has the right', 'can', 'permitted to',
            'अधिकार है', 'सकता है', 'अनुमति', 'स्वतंत्र है'
        ]
        self.prohibition_keywords = [
            'shall not', 'must not', 'prohibited from', 'may not', 'forbidden to',
            'नहीं करेगा', 'वर्जित', 'निषेध', 'प्रतिबंधित', 'मना है'
        ]
        self.condition_keywords = [
            'if', 'provided that', 'subject to', 'in the event',
            'यदि', 'बशर्ते', 'की स्थिति में', 'अधीन'
        ]
        self.definition_keywords = [
            'means', 'refers to', 'defined as', 'definition',
            'का अर्थ', 'तत्पर्य', 'परिभाषा'
        ]
    
    def extract(self, text: str) -> List[Dict]:
        """
        Extract clauses from contract text
        """
        clauses = []
        
        # Pre-process: Normalize newlines
        text = text.replace('\r\n', '\n')
        
        # Method 1: Split by numbered sections
        sections = re.split(self.clause_header_pattern, text)
        
        if len(sections) > 2:  # Found numbered sections
            clauses = self._process_numbered_sections(sections)
        
        # Fallback / Hybrid: If few clauses found, try paragraph splitting
        if len(clauses) < 2:
            clauses = self._process_paragraphs(text)
        
        # Classify each clause
        for i, clause in enumerate(clauses):
            clause['id'] = f"clause_{i+1}"
            clause['type'] = self._classify_clause(clause['text'])
            clause['word_count'] = len(clause['text'].split())
        
        return clauses
    
    def _process_numbered_sections(self, sections: List[str]) -> List[Dict]:
        """Process text split by numbered sections"""
        clauses = []
        # re.split with capturing group returns [pre, delimiter, match_group..., content, delimiter...]
        # Complex regex creates multiple groups
        
        current_header = "General"
        
        for part in sections:
            if not part: continue
            
            part = part.strip()
            # If it's a header (short, starts with number or 'Article')
            if len(part) < 100 and (part[0].isdigit() or part.lower().startswith('article')):
                current_header = part
            elif len(part) > 20: # Content
                clauses.append({
                    'header': current_header,
                    'text': part,
                    'full_text': f"{current_header}\n{part}"
                })
        
        return clauses
    
    def _process_paragraphs(self, text: str) -> List[Dict]:
        """Process text by splitting into paragraphs"""
        # Improved splitting: split by double newline OR newline followed by space/tab (indentation)
        paragraphs = re.split(r'\n\s*\n', text)
        clauses = []
        
        for para in paragraphs:
            para = para.strip()
            if len(para) > 20:  # Reduced threshold from 50 to 20
                clauses.append({
                    'header': para[:50] + '...' if len(para) > 50 else para,
                    'text': para,
                    'full_text': para
                })
        
        return clauses
    
    def _classify_clause(self, text: str) -> str:
        """
        Classify clause as obligation, right, prohibition, or condition
        """
        text_lower = text.lower()
        
        # Check for prohibitions first (more specific)
        for keyword in self.prohibition_keywords:
            if keyword in text_lower:
                return 'prohibition'
        
        # Check for obligations
        for keyword in self.obligation_keywords:
            if keyword in text_lower:
                return 'obligation'
        
        # Check for rights
        for keyword in self.right_keywords:
            if keyword in text_lower:
                return 'right'
        
        # Check for conditions
        if any(kw in text_lower for kw in self.condition_keywords):
            return 'condition'
        
        # Check for definitions
        if any(kw in text_lower for kw in self.definition_keywords):
            return 'definition'
        
        return 'general'
