const API_BASE = '/api';

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const uploadSection = document.getElementById('upload-section');
const resultsSection = document.getElementById('results-section');
const loader = document.getElementById('loader');
const resetBtn = document.getElementById('reset-btn');

// State
let currentContractId = null;
let currentClauses = [];

// Event Listeners
browseBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});

resetBtn.addEventListener('click', resetApp);

// Functions

function resetApp() {
    fileInput.value = '';
    uploadSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    // Clear data
    document.getElementById('summary-content').innerHTML = '';
    document.getElementById('risk-flags-content').innerHTML = '';
    document.getElementById('clauses-list').innerHTML = '';
}

async function handleFile(file) {
    // Show Loader
    document.querySelector('.upload-box').classList.add('hidden');
    loader.classList.remove('hidden');
    document.getElementById('loading-text').innerText = "Uploading document...";

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Step 1: Upload
        const uploadRes = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body: formData
        });

        if (!uploadRes.ok) throw new Error('Upload failed');
        const uploadData = await uploadRes.json();

        currentContractId = uploadData.contract_id;
        const text = uploadData.text;

        // Step 2: Analyze
        document.getElementById('loading-text').innerText = "Analyzing clauses and risks (AI)...";

        const analyzeRes = await fetch(`${API_BASE}/analyze/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contract_id: currentContractId,
                text: text
            })
        });

        if (!analyzeRes.ok) throw new Error('Analysis failed');
        const analysisData = await analyzeRes.json();

        renderResults(analysisData);

    } catch (error) {
        console.error(error);
        alert(`Error: ${error.message}`);
        resetApp();
    } finally {
        loader.classList.add('hidden');
        document.querySelector('.upload-box').classList.remove('hidden');
    }
}

function renderResults(data) {
    // Switch Views
    uploadSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Metrics
    document.getElementById('score-value').innerText = `${data.risk_score}/100`;
    document.getElementById('contract-type').innerText = titleCase(data.contract_type);
    document.getElementById('clause-count').innerText = data.clauses.length;

    // Risk Badge
    const badge = document.getElementById('risk-badge');
    badge.innerText = `${data.risk_level} RISK`;
    badge.className = `badge badge-${data.risk_level}`; // badge-high, badge-low

    // Summary (Markdown-ish parsing)
    document.getElementById('summary-content').innerHTML = parseMarkdown(data.summary);

    // Risk Flags
    const flagsContainer = document.getElementById('risk-flags-content');
    flagsContainer.innerHTML = '';
    if (data.risk_flags && data.risk_flags.length > 0) {
        data.risk_flags.forEach(flag => {
            const div = document.createElement('div');
            div.className = 'risk-flag';
            div.innerHTML = `
                <h4>${titleCase(flag.type.replace(/_/g, ' '))}</h4>
                <p>${flag.description}</p>
            `;
            flagsContainer.appendChild(div);
        });
    } else {
        flagsContainer.innerHTML = '<p class="text-muted">No critical risks detected.</p>';
    }

    // Recommendations
    const recList = document.querySelector('.rec-list');
    recList.innerHTML = '';
    if (data.recommendations) {
        data.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.innerText = rec;
            li.style.marginBottom = '0.5rem';
            recList.appendChild(li);
        });
    }

    // Clauses
    currentClauses = data.clauses;
    renderClauses(currentClauses);
}

function renderClauses(clauses) {
    const list = document.getElementById('clauses-list');
    list.innerHTML = '';

    clauses.forEach((clause, index) => {
        const riskClass = clause.risk_level === 'high' ? 'text-danger' :
            clause.risk_level === 'medium' ? 'text-warning' : 'text-success';

        const item = document.createElement('div');
        item.className = 'clause-item';

        const entitiesHtml = clause.entities ?
            Object.entries(clause.entities).map(([k, v]) =>
                `<span class="badge" style="background:#f1f5f9; color:#475569; margin-right:5px">${k}: ${v.length}</span>`
            ).join('') : '';

        item.innerHTML = `
            <div class="clause-header" onclick="toggleClause(this)">
                <div>
                    <strong>${clause.header || `Clause ${index + 1}`}</strong>
                    <span style="margin-left: 10px; font-size: 0.85rem; color: #64748b">${titleCase(clause.type)}</span>
                </div>
                <div style="display:flex; align-items:center; gap:10px">
                    ${entitiesHtml}
                    <span class="badge badge-${clause.risk_level}">${clause.risk_level.toUpperCase()}</span>
                    <i class="fa-solid fa-chevron-down"></i>
                </div>
            </div>
            <div class="clause-content">
                <div class="clause-text">"${clause.text}"</div>
                ${clause.deviation_flag ?
                `<div class="risk-flag" style="background:#fffbeb; border-color:#f59e0b">
                        <h4 style="color:#d97706">Standard Deviation</h4>
                        <p>This clause differs from standard templates.</p>
                        <p><strong>Suggestion:</strong> ${clause.suggested_match || 'N/A'}</p>
                     </div>` : ''
            }
            </div>
        `;
        list.appendChild(item);
    });
}

// Helper: Toggle Accordion
window.toggleClause = function (element) {
    const item = element.parentElement;
    item.classList.toggle('active');
    const icon = element.querySelector('.fa-chevron-down');
    if (item.classList.contains('active')) {
        icon.style.transform = 'rotate(180deg)';
    } else {
        icon.style.transform = 'rotate(0deg)';
    }
}

// Helper: Simple Markdown Parser
function parseMarkdown(text) {
    if (!text) return '';
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    return `<p>${html}</p>`;
}

function titleCase(str) {
    return str.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}
