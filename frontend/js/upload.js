// Upload Functionality for Brain Tumor Detection Frontend

class UploadManager {
    constructor() {
        this.uploadedFile = null;
        this.previewUrl = null;
        
        this.init();
    }

    /**
     * Initialize upload functionality
     */
    init() {
        this.setupEventListeners();
        console.log('Upload Manager initialized');
    }

    /**
     * Setup event listeners for file upload
     */
    setupEventListeners() {
        // File input change
        const fileInput = document.getElementById('mri-upload');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files[0]);
            });
        }

        // Upload area interactions
        this.setupDragAndDrop();
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        const uploadContent = document.querySelector('.upload-content');
        if (!uploadContent) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadContent.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop area
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadContent.addEventListener(eventName, () => {
                uploadContent.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadContent.addEventListener(eventName, () => {
                uploadContent.classList.remove('dragover');
            }, false);
        });

        // Handle dropped files
        uploadContent.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                this.handleFileSelection(files[0]);
            }
        }, false);

        // Click to upload
        uploadContent.addEventListener('click', () => {
            const fileInput = document.getElementById('mri-upload');
            if (fileInput) {
                fileInput.click();
            }
        });
    }

    /**
     * Prevent default drag behaviors
     * @param {Event} e - Event object
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Handle file selection
     * @param {File} file - Selected file
     */
    handleFileSelection(file) {
        if (!file) return;

        // Validate file
        const validation = FileUtils.validateFile(file);
        if (!validation.success) {
            UIUtils.showToast(validation.message, 'error');
            this.clearFileInput();
            return;
        }

        // Store file
        this.uploadedFile = file;
        
        // Display preview
        this.displayPreview(file);
        
        // Update UI
        this.updateUploadUI();
        
        // Notify app
        if (window.app) {
            window.app.selectedFile = file;
            window.app.updateAnalyzeButton();
        }

        UIUtils.showToast(`${file.name} uploaded successfully`, 'success');
    }

    /**
     * Display file preview
     * @param {File} file - File to preview
     */
    displayPreview(file) {
        // Create preview URL
        this.previewUrl = FileUtils.createPreview(file);
        
        // Get containers
        const uploadContent = document.querySelector('.upload-content');
        const previewContainer = document.getElementById('upload-preview');
        
        if (!uploadContent || !previewContainer) return;

        // Update preview container
        previewContainer.innerHTML = `
            <img src="${this.previewUrl}" alt="MRI Preview" />
            <div class="file-info">
                <strong>${file.name}</strong>
                <span>Size: ${FileUtils.formatFileSize(file.size)}</span>
                <span>Type: ${file.type}</span>
                <span>Last Modified: ${new Date(file.lastModified).toLocaleDateString()}</span>
            </div>
            <button type="button" class="remove-btn" onclick="uploadManager.removeFile()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Show/hide elements
        uploadContent.style.display = 'none';
        previewContainer.style.display = 'flex';
        
        // Add image load listener for better UX
        const img = previewContainer.querySelector('img');
        img.addEventListener('load', () => {
            img.style.opacity = '1';
        });
        
        img.addEventListener('error', () => {
            UIUtils.showToast('Failed to load image preview', 'warning');
        });
    }

    /**
     * Remove uploaded file
     */
    removeFile() {
        // Clean up preview URL
        if (this.previewUrl) {
            FileUtils.cleanupPreview(this.previewUrl);
            this.previewUrl = null;
        }

        // Clear file
        this.uploadedFile = null;

        // Reset UI
        this.resetUploadUI();
        
        // Clear file input
        this.clearFileInput();

        // Notify app
        if (window.app) {
            window.app.selectedFile = null;
            window.app.updateAnalyzeButton();
        }

        UIUtils.showToast('File removed', 'info');
    }

    /**
     * Update upload UI after successful upload
     */
    updateUploadUI() {
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn && window.app) {
            window.app.updateAnalyzeButton();
        }
    }

    /**
     * Reset upload UI to initial state
     */
    resetUploadUI() {
        const uploadContent = document.querySelector('.upload-content');
        const previewContainer = document.getElementById('upload-preview');
        
        if (uploadContent) uploadContent.style.display = 'block';
        if (previewContainer) {
            previewContainer.style.display = 'none';
            previewContainer.innerHTML = '';
        }
    }

    /**
     * Clear file input value
     */
    clearFileInput() {
        const fileInput = document.getElementById('mri-upload');
        if (fileInput) {
            fileInput.value = '';
        }
    }

    /**
     * Get uploaded file
     * @returns {File|null} - Uploaded file or null
     */
    getFile() {
        return this.uploadedFile;
    }

    /**
     * Check if file is uploaded
     * @returns {boolean} - True if file is uploaded
     */
    hasFile() {
        return this.uploadedFile !== null;
    }

    /**
     * Validate current file
     * @returns {object} - Validation result
     */
    validateCurrentFile() {
        if (!this.uploadedFile) {
            return { success: false, message: 'No file selected' };
        }

        return FileUtils.validateFile(this.uploadedFile);
    }

    /**
     * Get file information
     * @returns {object|null} - File information or null
     */
    getFileInfo() {
        if (!this.uploadedFile) return null;

        return {
            name: this.uploadedFile.name,
            size: this.uploadedFile.size,
            type: this.uploadedFile.type,
            lastModified: this.uploadedFile.lastModified,
            formattedSize: FileUtils.formatFileSize(this.uploadedFile.size)
        };
    }

    /**
     * Reset upload manager
     */
    reset() {
        this.removeFile();
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        if (this.previewUrl) {
            FileUtils.cleanupPreview(this.previewUrl);
        }
        
        this.uploadedFile = null;
        this.previewUrl = null;
        
        console.log('Upload Manager cleanup completed');
    }
}

// Initialize upload manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if main app is not handling uploads
    if (!window.app) {
        window.uploadManager = new UploadManager();
    } else {
        console.log('Upload handling delegated to main app');
    }
});

// Export for external access
window.UploadManager = UploadManager;