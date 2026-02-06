"""
Entity Extractor - Extract named entities from contract text
"""
import spacy
from typing import Dict, List
import re

class EntityExtractor:
    """Extract legal entities (parties, dates, amounts, jurisdiction, etc.)"""
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            print("Warning: en_core_web_lg not found. Install with: python -m spacy download en_core_web_lg")
            self.nlp = None
    
    def extract(self, text: str) -> Dict[str, List]:
        """
        Extract all legal entities from text
        
        Returns:
            Dict with entity types: parties, dates, amounts, jurisdiction, etc.
        """
        entities = {
            'parties': [],
            'dates': [],
            'amounts': [],
            'jurisdiction': [],
            'durations': [],
            'locations': []
        }
        
        if not self.nlp:
            return entities
        
        doc = self.nlp(text)
        
        # Extract using spaCy NER
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG']:
                entities['parties'].append({
                    'text': ent.text,
                    'type': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            elif ent.label_ == 'DATE':
                entities['dates'].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            elif ent.label_ == 'MONEY':
                entities['amounts'].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            elif ent.label_ in ['GPE', 'LOC']:
                entities['locations'].append({
                    'text': ent.text,
                    'type': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
        
        # Extract jurisdiction-specific patterns
        entities['jurisdiction'] = self._extract_jurisdiction(text)
        
        # Extract durations (e.g., "2 years", "6 months")
        entities['durations'] = self._extract_durations(text)
        
        # Deduplicate
        for key in entities:
            entities[key] = self._deduplicate_entities(entities[key])
        
        return entities
    
    def _extract_jurisdiction(self, text: str) -> List[Dict]:
        """Extract jurisdiction and governing law mentions"""
        jurisdiction_patterns = [
            r'governed by.*?laws of ([^,\.]+)',
            r'jurisdiction of ([^,\.]+)',
            r'courts? (?:of|in) ([^,\.]+)',
            r'arbitration in ([^,\.]+)'
        ]
        
        jurisdictions = []
        for pattern in jurisdiction_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                jurisdictions.append({
                    'text': match.group(1).strip(),
                    'context': match.group(0),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return jurisdictions
    
    def _extract_durations(self, text: str) -> List[Dict]:
        """Extract time durations (lock-in periods, notice periods, etc.)"""
        duration_pattern = r'\b(\d+)\s+(day|week|month|year)s?\b'
        
        durations = []
        matches = re.finditer(duration_pattern, text, re.IGNORECASE)
        for match in matches:
            durations.append({
                'text': match.group(0),
                'value': int(match.group(1)),
                'unit': match.group(2).lower(),
                'start': match.start(),
                'end': match.end()
            })
        
        return durations
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities based on text"""
        seen = set()
        unique = []
        for entity in entities:
            text = entity.get('text', '').lower().strip()
            if text and text not in seen:
                seen.add(text)
                unique.append(entity)
        return unique
