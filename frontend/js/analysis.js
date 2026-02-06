/**
 * Analysis Results Display
 */

/**
 * Display analysis results
 */
function displayAnalysisResults(analysis) {
    // Show results section
    showSection('results-section');
    
    // Update overview
    document.getElementById('contract-type').textContent = 
        analysis.contract_type.charAt(0).toUpperCase() + analysis.contract_type.slice(1);
    
    document.getElementById('risk-score').textContent = 
        `${analysis.risk_score}/100`;
    
    document.getElementById('clause-count').textContent = 
        analysis.clauses.length;
    
    // Update risk indicator
    const riskIndicator = document.getElementById('risk-indicator');
    riskIndicator.className = `risk-indicator ${analysis.risk_level}`;
    
    // Update summary
    document.getElementById('summary-content').textContent = 
        analysis.summary || 'Analysis complete. Review details below.';
    
    // Display risk flags
    displayRiskFlags(analysis.risk_flags);
    
    // Display recommendations
    displayRecommendations(analysis.recommendations);
    
    // Display clauses
    displayClauses(analysis.clauses);
    
    // Setup action buttons
    setupActionButtons();
}

/**
 * Display risk flags
 */
function displayRiskFlags(flags) {
    const container = document.getElementById('risk-flags-list');
    container.innerHTML = '';
    
    if (!flags || flags.length === 0) {
        container.innerHTML = '<p style="color: #27ae60;">No major risk flags detected</p>';
        return;
    }
    
    flags.forEach(flag => {
        const flagDiv = document.createElement('div');
        flagDiv.className = 'risk-flag high';
        flagDiv.innerHTML = `
            <h4>${flag.type.replace(/_/g, ' ').toUpperCase()}</h4>
            <p>${flag.description}</p>
        `;
        container.appendChild(flagDiv);
    });
}

/**
 * Display recommendations
 */
function displayRecommendations(recommendations) {
    const list = document.getElementById('recommendations-list');
    list.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        list.innerHTML = '<li>Review contract with legal counsel</li>';
        return;
    }
    
    recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        list.appendChild(li);
    });
}

/**
 * Display clauses
 */
function displayClauses(clauses) {
    const container = document.getElementById('clauses-container');
    container.innerHTML = '';
    
    if (!clauses || clauses.length === 0) {
        container.innerHTML = '<p>No clauses extracted</p>';
        return;
    }
    
    clauses.forEach((clause, index) => {
        const clauseDiv = document.createElement('div');
        clauseDiv.className = 'clause-item';
        clauseDiv.innerHTML = `
            <div class="clause-header">
                <span class="clause-id">Clause ${index + 1}</span>
                <span class="clause-risk ${clause.risk_level || 'low'}">
                    ${(clause.risk_level || 'low').toUpperCase()}
                </span>
            </div>
            <div class="clause-type">${clause.type || 'general'}</div>
            <p class="clause-text">${clause.text.substring(0, 300)}${clause.text.length > 300 ? '...' : ''}</p>
            ${clause.entities && clause.entities.parties && clause.entities.parties.length > 0 ? 
                `<div style="margin-top: 10px; font-size: 0.9rem; color: #7f8c8d;">
                    <strong>Parties:</strong> ${clause.entities.parties.map(p => p.text).join(', ')}
                </div>` : ''
            }
        `;
        
        // Add click handler for detailed view
        clauseDiv.addEventListener('click', () => showClauseDetails(clause, index + 1));
        
        container.appendChild(clauseDiv);
    });
}

/**
 * Show detailed clause analysis
 */
function showClauseDetails(clause, clauseNumber) {
    // Create modal or expand view
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 20px;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        max-width: 800px;
        max-height: 80vh;
        overflow-y: auto;
        border-radius: 12px;
        padding: 30px;
    `;
    
    content.innerHTML = `
        <h2>Clause ${clauseNumber} - Detailed Analysis</h2>
        <div style="margin: 20px 0;">
            <span class="clause-risk ${clause.risk_level}">${clause.risk_level.toUpperCase()} RISK</span>
            <span class="clause-type" style="margin-left: 10px;">${clause.type}</span>
        </div>
        <h3>Full Text:</h3>
        <p style="background: #f8f9fa; padding: 15px; border-radius: 6px; line-height: 1.8;">
            ${clause.text}
        </p>
        <button class="btn btn-secondary" style="margin-top: 20px;" onclick="this.closest('.modal').remove()">
            Close
        </button>
    `;
    
    modal.className = 'modal';
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

/**
 * Setup action buttons
 */
function setupActionButtons() {
    // Export PDF
    document.getElementById('export-pdf-btn').onclick = async () => {
        try {
            showNotification('Generating PDF report...', 'info');
            
            const response = await fetch(`${API_BASE_URL}/export/pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contract_id: currentContractId,
                    analysis: currentAnalysis
                })
            });
            
            if (!response.ok) {
                throw new Error('PDF export failed');
            }
            
            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `contract_analysis_${currentContractId}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            
            showNotification('PDF report downloaded!', 'success');
            
        } catch (error) {
            console.error('Export error:', error);
            showNotification(error.message, 'error');
        }
    };
    
    // New analysis
    document.getElementById('new-analysis-btn').onclick = () => {
        resetApp();
        showNotification('Ready for new analysis', 'info');
    };
}
