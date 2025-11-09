// Main Application Logic for Brain Tumor Detection Frontend

class BrainTumorApp {
    constructor() {
        this.currentPage = 'analysis';
        this.backendStatus = false;
        this.selectedFile = null;
        this.analysisResults = null;
        
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.checkBackendStatus();
        this.showPage('analysis');
        
        console.log('Brain Tumor Detection App initialized');
    }

    /**
     * Setup event listeners for the application
     */
    setupEventListeners() {
        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-btn')) {
                const page = e.target.dataset.page;
                this.showPage(page);
            }
        });

        // Form submission
        const patientForm = document.getElementById('patient-form');
        if (patientForm) {
            patientForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmission();
            });
        }

        // File upload handling
        this.setupFileUpload();

        // Analysis button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.analyzeImage();
            });
        }

        // Window events
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === '1') {
                e.preventDefault();
                this.showPage('analysis');
            } else if (e.ctrlKey && e.key === '2') {
                e.preventDefault();
                this.showPage('chat');
            }
        });
    }

    /**
     * Setup file upload functionality
     */
    setupFileUpload() {
        const uploadArea = document.querySelector('.upload-content');
        const fileInput = document.getElementById('mri-upload');
        
        if (!uploadArea || !fileInput) {
            console.warn('Upload elements not found:', { uploadArea: !!uploadArea, fileInput: !!fileInput });
            return;
        }

        console.log('Setting up file upload functionality');

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileSelection(file);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelection(files[0]);
            }
        });
    }

    /**
     * Handle file selection
     * @param {File} file - Selected file
     */
    handleFileSelection(file) {
        console.log('File selected:', file);
        
        const validation = FileUtils.validateFile(file);
        console.log('File validation result:', validation);
        
        if (!validation.success) {
            UIUtils.showToast(validation.message, 'error');
            return;
        }

        this.selectedFile = file;
        this.displayFilePreview(file);
        this.updateAnalyzeButton();
        
        UIUtils.showToast('MRI image uploaded successfully', 'success');
    }

    /**
     * Display file preview
     * @param {File} file - File to preview
     */
    displayFilePreview(file) {
        const uploadContent = document.querySelector('.upload-content');
        const previewContainer = document.getElementById('upload-preview');
        const previewImage = document.getElementById('preview-image');
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');
        const fileType = document.getElementById('file-type');
        
        if (!uploadContent || !previewContainer) {
            console.error('Upload elements not found for preview');
            return;
        }

        console.log('Displaying file preview for:', file.name);

        // Create preview URL
        const previewUrl = FileUtils.createPreview(file);
        
        // Update existing elements
        if (previewImage) previewImage.src = previewUrl;
        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = `Size: ${FileUtils.formatFileSize(file.size)}`;
        if (fileType) fileType.textContent = `Type: ${file.type}`;
        
        // Show preview, hide upload area
        uploadContent.style.display = 'none';
        previewContainer.style.display = 'flex';
    }

    /**
     * Remove selected file
     */
    removeSelectedFile() {
        console.log('Removing selected file');
        
        if (this.selectedFile) {
            // Clean up preview URL
            const preview = document.querySelector('#upload-preview img');
            if (preview && preview.src) {
                FileUtils.cleanupPreview(preview.src);
            }
        }

        this.selectedFile = null;
        
        // Reset UI elements
        const uploadContent = document.querySelector('.upload-content');
        const previewContainer = document.getElementById('upload-preview');
        const fileInput = document.getElementById('mri-upload');
        const previewImage = document.getElementById('preview-image');
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');
        const fileType = document.getElementById('file-type');
        
        // Show upload area, hide preview
        if (uploadContent) uploadContent.style.display = 'block';
        if (previewContainer) previewContainer.style.display = 'none';
        
        // Clear file input
        if (fileInput) fileInput.value = '';
        
        // Clear preview elements
        if (previewImage) previewImage.src = '';
        if (fileName) fileName.textContent = '';
        if (fileSize) fileSize.textContent = '';
        if (fileType) fileType.textContent = '';
        
        this.updateAnalyzeButton();
        
        UIUtils.showToast('File removed', 'info');
    }

    /**
     * Update analyze button state
     */
    updateAnalyzeButton() {
        const analyzeBtn = document.getElementById('analyze-btn');
        const form = document.getElementById('patient-form');
        
        if (!analyzeBtn) return;
        
        const formData = FormUtils.extractFormData(form);
        const formValid = FormUtils.validatePatientForm(formData).success;
        const fileValid = this.selectedFile !== null;
        const backendOnline = this.backendStatus;
        
        const isEnabled = formValid && fileValid && backendOnline;
        
        analyzeBtn.disabled = !isEnabled;
        
        if (!backendOnline) {
            analyzeBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Backend Offline';
        } else if (!formValid) {
            analyzeBtn.innerHTML = '<i class="fas fa-form"></i> Complete Form';
        } else if (!fileValid) {
            analyzeBtn.innerHTML = '<i class="fas fa-upload"></i> Upload MRI Image';
        } else {
            analyzeBtn.innerHTML = '<i class="fas fa-brain"></i> Analyze MRI';
        }
    }

    /**
     * Handle form submission
     */
    handleFormSubmission() {
        const form = document.getElementById('patient-form');
        const formData = FormUtils.extractFormData(form);
        const validation = FormUtils.validatePatientForm(formData);
        
        if (!validation.success) {
            validation.errors.forEach(error => {
                UIUtils.showToast(error, 'error');
            });
            return;
        }
        
        this.updateAnalyzeButton();
        UIUtils.showToast('Patient information saved', 'success');
    }

    /**
     * Analyze MRI image
     */
    async analyzeImage() {
        if (!this.selectedFile) {
            UIUtils.showToast('Please select an MRI image', 'error');
            return;
        }

        const form = document.getElementById('patient-form');
        const formData = FormUtils.extractFormData(form);
        const validation = FormUtils.validatePatientForm(formData);
        
        if (!validation.success) {
            UIUtils.showToast('Please complete the patient form', 'error');
            return;
        }

        try {
            UIUtils.toggleLoading(true, 'Analyzing MRI Image...');
            
            // Simulate progress updates
            this.simulateProgress();
            
            // Prepare form data for API
            const apiFormData = APIUtils.createFormData(formData, this.selectedFile);
            
            // Make API request
            const response = await APIUtils.makeRequest(
                `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PREDICTION}`,
                {
                    method: 'POST',
                    body: apiFormData
                }
            );
            
            const results = await response.json();
            
            UIUtils.toggleLoading(false);
            
            this.analysisResults = results;
            this.displayResults(results);
            this.scrollToResults();
            
            UIUtils.showToast('Analysis completed successfully!', 'success');
            
        } catch (error) {
            console.error('Analysis error:', error);
            UIUtils.toggleLoading(false);
            UIUtils.showToast(`Analysis failed: ${error.message}`, 'error');
        }
    }

    /**
     * Simulate progress for better UX
     */
    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 95) {
                progress = 95;
                clearInterval(interval);
            }
            UIUtils.updateProgress(Math.round(progress));
        }, 200);
    }

    /**
     * Display analysis results
     * @param {object} results - Analysis results from API
     */
    displayResults(results) {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');
        
        if (!resultsSection || !resultsContent) return;

        // Show results section
        resultsSection.style.display = 'block';
        
        // Get risk level
        const riskLevel = MedicalUtils.getRiskLevel(
            results.confidence, 
            results.prediction
        );
        
        // Create results HTML
        resultsContent.innerHTML = `
            <div class="result-summary">
                <div class="result-card primary">
                    <i class="fas fa-brain"></i>
                    <h4>Prediction</h4>
                    <div class="value">${MedicalUtils.formatPrediction(results.prediction)}</div>
                </div>
                <div class="result-card ${this.getConfidenceClass(results.confidence)}">
                    <i class="fas fa-chart-line"></i>
                    <h4>Confidence</h4>
                    <div class="value">${MedicalUtils.formatConfidence(results.confidence)}</div>
                </div>
                <div class="result-card ${this.getRiskClass(riskLevel)}">
                    <i class="fas fa-shield-alt"></i>
                    <h4>Risk Level</h4>
                    <div class="value">${riskLevel.label}</div>
                </div>
                <div class="result-card success">
                    <i class="fas fa-clock"></i>
                    <h4>Analysis Time</h4>
                    <div class="value">${results.analysis_time || '< 1s'}</div>
                </div>
            </div>
            
            <div class="probabilities">
                <h4><i class="fas fa-percentage"></i> Class Probabilities</h4>
                ${this.createProbabilityBars(results.probabilities)}
            </div>
            
            <div class="medical-info">
                <h4><i class="fas fa-info-circle"></i> Medical Information</h4>
                <p>${MedicalUtils.getTumorDescription(results.prediction)}</p>
                
                <h5><i class="fas fa-lightbulb"></i> Recommendations</h5>
                <ul>
                    ${MedicalUtils.generateRecommendations(results.prediction, results.confidence)
                        .map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
            
            <div class="report-section">
                <h4><i class="fas fa-file-pdf"></i> Medical Report</h4>
                <p>Generate a detailed PDF report with complete analysis results.</p>
                <button 
                    class="download-btn" 
                    onclick="app.downloadReport()"
                    ${!results.report_filename ? 'disabled' : ''}
                >
                    <i class="fas fa-download"></i>
                    Download PDF Report
                </button>
            </div>
        `;
        
        // Animate counters
        this.animateResultCounters();
    }

    /**
     * Create probability bars HTML
     * @param {object} probabilities - Probability scores
     * @returns {string} - HTML string
     */
    createProbabilityBars(probabilities) {
        return Object.entries(probabilities)
            .map(([label, probability]) => `
                <div class="probability-item">
                    <span class="probability-label">${label}</span>
                    <div class="probability-bar">
                        <div 
                            class="probability-fill" 
                            style="width: ${(probability * 100).toFixed(1)}%"
                        ></div>
                    </div>
                    <span class="probability-value">${MedicalUtils.formatConfidence(probability)}</span>
                </div>
            `).join('');
    }

    /**
     * Get CSS class for confidence level
     * @param {number} confidence - Confidence score
     * @returns {string} - CSS class name
     */
    getConfidenceClass(confidence) {
        if (confidence >= MEDICAL_CONFIG.CONFIDENCE_THRESHOLDS.HIGH) return 'success';
        if (confidence >= MEDICAL_CONFIG.CONFIDENCE_THRESHOLDS.MEDIUM) return 'warning';
        return 'danger';
    }

    /**
     * Get CSS class for risk level
     * @param {object} riskLevel - Risk level object
     * @returns {string} - CSS class name
     */
    getRiskClass(riskLevel) {
        if (riskLevel.label.includes('Low')) return 'success';
        if (riskLevel.label.includes('Moderate')) return 'warning';
        return 'danger';
    }

    /**
     * Animate result counters
     */
    animateResultCounters() {
        setTimeout(() => {
            const valueElements = document.querySelectorAll('.result-card .value');
            valueElements.forEach(element => {
                const text = element.textContent;
                if (text.includes('%')) {
                    const value = parseFloat(text.replace('%', ''));
                    element.textContent = '0%';
                    UIUtils.animateCounter(element, 0, value, 1000);
                    setTimeout(() => {
                        element.textContent = text;
                    }, 1000);
                }
            });
        }, 100);
    }

    /**
     * Download PDF report
     */
    async downloadReport() {
        if (!this.analysisResults?.report_filename) {
            UIUtils.showToast('No report available for download', 'error');
            return;
        }

        try {
            UIUtils.toggleLoading(true, 'Generating Report...');
            
            const response = await APIUtils.makeRequest(
                `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REPORT}/${this.analysisResults.report_filename}`
            );
            
            const blob = await response.blob();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.analysisResults.report_filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            UIUtils.toggleLoading(false);
            UIUtils.showToast('Report downloaded successfully', 'success');
            
        } catch (error) {
            console.error('Download error:', error);
            UIUtils.toggleLoading(false);
            UIUtils.showToast(`Download failed: ${error.message}`, 'error');
        }
    }

    /**
     * Scroll to results section
     */
    scrollToResults() {
        const resultsSection = document.getElementById('results-section');
        if (resultsSection) {
            UIUtils.scrollToElement(resultsSection);
        }
    }

    /**
     * Show specific page
     * @param {string} pageId - Page identifier
     */
    showPage(pageId) {
        // Update current page
        this.currentPage = pageId;
        
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show selected page
        const targetPage = document.getElementById(`${pageId}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }
        
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-page="${pageId}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
        // Page-specific initialization
        if (pageId === 'chat') {
            // Initialize chat if not already done
            if (window.chatManager) {
                window.chatManager.initializeChat();
            } else {
                // Wait a bit for chat manager to load
                setTimeout(() => {
                    if (window.chatManager) {
                        window.chatManager.initializeChat();
                    }
                }, 100);
            }
        }
    }

    async checkBackendStatus() {
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`, {
                method: 'GET',
                signal: AbortSignal.timeout(5000)  
            });
            
            this.backendStatus = response.ok;
            this.updateStatusIndicator(response.ok);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Backend status:', data);
                UIUtils.showToast('Connected to backend server', 'success');
            } else {
                console.warn('Backend health check failed:', response.status);
                UIUtils.showToast('Backend server issues detected', 'warning');
            }
            
        } catch (error) {
            console.error('Backend status check failed:', error);
            this.backendStatus = false;
            this.updateStatusIndicator(false);
            
        }
        
        
        this.updateAnalyzeButton();
        
        
        setTimeout(() => {
            this.checkBackendStatus();
        }, 30000); // 
    }


    cleanup() {
        
        if (this.selectedFile) {
            const preview = document.querySelector('#upload-preview img');
            if (preview) {
                FileUtils.cleanupPreview(preview.src);
            }
        }
        
        console.log('App cleanup completed');
    }
}


document.addEventListener('DOMContentLoaded', () => {
    window.app = new BrainTumorApp();
});


window.BrainTumorApp = BrainTumorApp;