# Legal Contract Assistant

AI-powered legal assistant for Indian SMEs to analyze contracts, identify risks, and receive actionable advice.

## Features

- **Contract Analysis**: Upload PDF, DOCX, or TXT contracts
- **Risk Assessment**: Clause-by-clause risk scoring (Low/Medium/High)
- **Entity Extraction**: Identify parties, dates, amounts, jurisdiction
- **Risk Scoring**: Composite contract risk score (0-100)
- **Plain Language**: SME-friendly explanations (no legal jargon)
- **PDF Reports**: Export analysis for legal review
- **Indian Context**: Focus on Indian Contract Act compliance
- **Confidential**: Local processing, no cloud storage

## Supported Contract Types

- Employment Agreements
- Vendor Contracts
- Lease Agreements
- Partnership Deeds
- Service Contracts

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for serving frontend) or any static file server
- Groq API key (free tier available at https://console.groq.com)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CHELLAM_GUVI
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy models**
   ```bash
   python -m spacy download en_core_web_lg
   python -m spacy download xx_ent_wiki_sm
   ```

4. **Set up Groq API key**
   - Get your free API key from https://console.groq.com/keys
   - Update the `.env` file:
   ```bash
   GROQ_API_KEY=your-groq-api-key-here
   ```

### Running the Application

1. **Start the App**
   ```bash
   python backend/app.py
   ```
   The application will open can be accessed in your browser at http://localhost:5000


## Usage

1. **Upload Contract**: Drag & drop or select a contract file (PDF, DOCX, TXT)
2. **Wait for Analysis**: The system will extract clauses and assess risks
3. **Review Results**: 
   - Overall risk score and contract type
   - Clause-by-clause breakdown
   - Risk flags and recommendations
4. **Export Report**: Download PDF report for legal consultation

## Project Structure

```
.
├── backend/
│   ├── app.py                 # Flask application
│   ├── routes/                # API endpoints
│   ├── nlp/                   # NLP processing
│   ├── llm/                   # GPT-4 integration
│   └── utils/                 # Utilities (logging, PDF export)
├── frontend/
│   ├── index.html             # Main UI
│   ├── css/                   # Styles
│   └── js/                    # JavaScript logic
├── data/
│   ├── contracts/             # Sample contracts
│   ├── uploads/               # Uploaded files
│   ├── reports/               # Generated reports
│   └── audit_logs/            # Audit trails
├── tests/                     # Test suite
└── requirements.txt           # Python dependencies
```

## API Endpoints

- `GET /` - Health check
- `POST /api/upload/` - Upload contract
- `POST /api/analyze/` - Analyze contract
- `POST /api/analyze/clause/<id>` - Analyze specific clause
- `POST /api/export/pdf` - Export PDF report
- `POST /api/export/json` - Export JSON data

## Testing

```bash
pytest tests/ -v
```

## Risk Assessment Logic

### Clause-Level Risks
- **HIGH (70-100)**: Unilateral termination, uncapped liability, IP transfer, >2yr non-compete
- **MEDIUM (40-69)**: Ambiguous terms, one-sided penalties, auto-renewal
- **LOW (0-39)**: Standard clauses, balanced terms

### Risk Flags Detected
- Penalty clauses >20% of contract value
- Uncapped indemnity
- Unilateral termination rights
- Inconvenient jurisdiction
- Auto-renewal with lock-in >1 year
- Non-compete >1 year
- Automatic IP transfer

## Limitations

- **Text-based PDFs only**: No OCR for scanned documents
- **English/Hindi**: Limited multilingual support
- **No external legal data**: No case law or statute APIs
- **AI limitations**: Not a substitute for legal counsel

## Disclaimer

**This tool provides AI-generated analysis and is NOT legal advice.** Always consult a qualified legal professional before making decisions based on this analysis.

## Technology Stack

- **Backend**: Python, Flask, spaCy, NLTK
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Document Parsing**: PyPDF2, python-docx
- **Reporting**: ReportLab

## License

[Add your license here]

## Contributing

[Add contribution guidelines]

## Support

For issues or questions, please [create an issue](link-to-issues) or contact [your-email].
