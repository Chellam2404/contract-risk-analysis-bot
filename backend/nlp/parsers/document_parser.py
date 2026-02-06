"""
Document Parser - Extract text from PDF, DOCX, and TXT files
"""
import os
from typing import Dict

class DocumentParser:
    """Parse various document formats and extract text"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'docx', 'txt']
    
    def parse(self, filepath: str, file_extension: str) -> Dict:
        """
        Parse document and extract text
        
        Args:
            filepath: Path to the document
            file_extension: File extension (pdf, docx, txt)
            
        Returns:
            Dict with 'success', 'text', and optional 'error'
        """
        try:
            if file_extension == 'pdf':
                return self._parse_pdf(filepath)
            elif file_extension == 'docx':
                return self._parse_docx(filepath)
            elif file_extension == 'txt':
                return self._parse_txt(filepath)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported format: {file_extension}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Parsing error: {str(e)}'
            }
    
    def _parse_pdf(self, filepath: str) -> Dict:
        """Extract text from PDF (text-based only, no OCR)"""
        try:
            import PyPDF2
            
            text = ""
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF has text
                if len(pdf_reader.pages) == 0:
                    return {
                        'success': False,
                        'error': 'PDF has no pages'
                    }
                
                # Extract text from all pages
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                
                # Validate extraction
                if len(text.strip()) < 100:
                    return {
                        'success': False,
                        'error': 'PDF appears to be scanned/image-based. Only text-based PDFs are supported.'
                    }
                
                return {
                    'success': True,
                    'text': text.strip()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF parsing failed: {str(e)}'
            }
    
    def _parse_docx(self, filepath: str) -> Dict:
        """Extract text from DOCX file"""
        try:
            from docx import Document
            
            doc = Document(filepath)
            text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
            if len(text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'DOCX appears to be empty or unreadable'
                }
            
            return {
                'success': True,
                'text': text.strip()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'DOCX parsing failed: {str(e)}'
            }
    
    def _parse_txt(self, filepath: str) -> Dict:
        """Extract text from plain text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if len(text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Text file appears to be empty'
                }
            
            return {
                'success': True,
                'text': text.strip()
            }
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as file:
                    text = file.read()
                return {
                    'success': True,
                    'text': text.strip()
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Text file encoding error: {str(e)}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Text file parsing failed: {str(e)}'
            }
