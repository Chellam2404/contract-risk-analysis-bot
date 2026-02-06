/**
 * File Upload Handling
 */

const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');

// Drag and drop handlers
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Upload button click
uploadBtn.addEventListener('click', () => {
    const file = fileInput.files[0];
    if (file) {
        uploadContract(file);
    }
});

/**
 * Handle file selection
 */
function handleFileSelect(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const allowedExtensions = ['.pdf', '.docx', '.txt'];
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showNotification('Invalid file type. Please upload PDF, DOCX, or TXT file.', 'error');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showNotification('File too large. Maximum size is 16MB.', 'error');
        return;
    }
    
    // Update UI
    document.getElementById('filename').textContent = file.name;
    document.getElementById('filesize').textContent = formatFileSize(file.size);
    showSection('file-info');
}

/**
 * Upload contract to backend
 */
async function uploadContract(file) {
    // Show progress
    showSection('upload-progress');
    hideSection('file-info');
    
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Upload file
        progressText.textContent = 'Uploading contract...';
        progressFill.style.width = '30%';
        
        const uploadResponse = await fetch(`${API_BASE_URL}/upload/`, {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            const error = await uploadResponse.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const uploadData = await uploadResponse.json();
        currentContractId = uploadData.contract_id;
        
        progressFill.style.width = '60%';
        progressText.textContent = 'Analyzing contract...';
        
        // Analyze contract
        const analyzeResponse = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contract_id: currentContractId,
                text: uploadData.text_preview  // In real app, send full text
            })
        });
        
        if (!analyzeResponse.ok) {
            const error = await analyzeResponse.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        currentAnalysis = await analyzeResponse.json();
        
        progressFill.style.width = '100%';
        progressText.textContent = 'Complete!';
        
        // Show results
        setTimeout(() => {
            hideSection('upload-section');
            displayAnalysisResults(currentAnalysis);
        }, 500);
        
        showNotification('Contract analyzed successfully!', 'success');
        
    } catch (error) {
        console.error('Upload/Analysis error:', error);
        showNotification(error.message, 'error');
        
        // Reset UI
        hideSection('upload-progress');
        showSection('file-info');
    }
}
