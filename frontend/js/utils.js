// Utility Functions for Brain Tumor Detection Frontend

/**
 * File validation and handling utilities
 */
const FileUtils = {
    /**
     * Validate uploaded file
     * @param {File} file - File object to validate
     * @returns {object} - Validation result with success boolean and message
     */
    validateFile(file) {
        if (!file) {
            return { success: false, message: 'Please select a file' };
        }

        // Check file type
        if (!UI_CONFIG.ALLOWED_FILE_TYPES.includes(file.type)) {
            return { 
                success: false, 
                message: 'Please upload a valid image file (JPEG, PNG, GIF, TIFF)' 
            };
        }

        // Check file size
        if (file.size > UI_CONFIG.MAX_FILE_SIZE) {
            const maxSizeMB = UI_CONFIG.MAX_FILE_SIZE / (1024 * 1024);
            return { 
                success: false, 
                message: `File size must be less than ${maxSizeMB}MB` 
            };
        }

        return { success: true, message: 'File is valid' };
    },

    /**
     * Format file size for display
     * @param {number} bytes - File size in bytes
     * @returns {string} - Formatted file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Create preview URL for image file
     * @param {File} file - Image file
     * @returns {string} - Object URL for preview
     */
    createPreview(file) {
        return URL.createObjectURL(file);
    },

    /**
     * Clean up preview URL
     * @param {string} url - Object URL to revoke
     */
    cleanupPreview(url) {
        if (url) {
            URL.revokeObjectURL(url);
        }
    }
};

/**
 * Form validation utilities
 */
const FormUtils = {
    /**
     * Validate patient form data
     * @param {object} formData - Form data object
     * @returns {object} - Validation result
     */
    validatePatientForm(formData) {
        const errors = [];

        if (!formData.name || formData.name.trim().length < 2) {
            errors.push('Patient name must be at least 2 characters');
        }

        if (!formData.age || formData.age < 1 || formData.age > 150) {
            errors.push('Please enter a valid age between 1 and 150');
        }

        if (!formData.gender) {
            errors.push('Please select patient gender');
        }

        return {
            success: errors.length === 0,
            errors: errors
        };
    },

    /**
     * Extract form data from form element
     * @param {HTMLFormElement} form - Form element
     * @returns {object} - Form data object
     */
    extractFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    },

    /**
     * Reset form and clear validation errors
     * @param {HTMLFormElement} form - Form to reset
     */
    resetForm(form) {
        form.reset();
        
        // Clear custom validation styles
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.classList.remove('error', 'success');
        });
    }
};

/**
 * API utilities for HTTP requests
 */
const APIUtils = {
    /**
     * Make HTTP request with retry logic
     * @param {string} url - Request URL
     * @param {object} options - Fetch options
     * @param {number} retryCount - Current retry attempt
     * @returns {Promise} - Response promise
     */
    async makeRequest(url, options = {}, retryCount = 0) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return response;
        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                throw new Error('Request timed out. Please try again.');
            }

            // Retry logic for network errors
            if (retryCount < API_CONFIG.RETRY_ATTEMPTS && this.isRetryableError(error)) {
                await this.delay(API_CONFIG.RETRY_DELAY * (retryCount + 1));
                return this.makeRequest(url, options, retryCount + 1);
            }

            throw error;
        }
    },

    /**
     * Check if error is retryable
     * @param {Error} error - Error object
     * @returns {boolean} - Whether error is retryable
     */
    isRetryableError(error) {
        return error.name === 'TypeError' || // Network error
               error.message.includes('Failed to fetch') ||
               error.message.includes('NetworkError');
    },

    /**
     * Delay utility for retry logic
     * @param {number} ms - Milliseconds to delay
     * @returns {Promise} - Delay promise
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * Create FormData for file upload
     * @param {object} data - Data object
     * @param {File} file - File to upload
     * @returns {FormData} - FormData object
     */
    createFormData(data, file) {
        const formData = new FormData();
        
        // Add patient data
        Object.keys(data).forEach(key => {
            if (data[key] !== undefined && data[key] !== null) {
                formData.append(key, data[key]);
            }
        });
        
        // Add file
        if (file) {
            formData.append('file', file);
        }
        
        return formData;
    }
};

/**
 * UI utilities for DOM manipulation and feedback
 */
const UIUtils = {
    /**
     * Show toast notification
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds
     */
    showToast(message, type = 'info', duration = UI_CONFIG.TOAST_DURATION) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <i class="${icon}"></i>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
        `;
        
        // Add to container
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration);
        
        // Allow manual close on click
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    },

    /**
     * Get icon for toast type
     * @param {string} type - Toast type
     * @returns {string} - Icon class name
     */
    getToastIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    },

    /**
     * Show/hide loading overlay
     * @param {boolean} show - Whether to show loading
     * @param {string} message - Loading message
     * @param {number} progress - Progress percentage (0-100)
     */
    toggleLoading(show, message = 'Processing...', progress = null) {
        let overlay = document.getElementById('loading-overlay');
        
        if (show) {
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'loading-overlay';
                overlay.className = 'loading-overlay';
                document.body.appendChild(overlay);
            }
            
            overlay.innerHTML = `
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <h3>${message}</h3>
                    <p>Please wait while we analyze your MRI scan...</p>
                    ${progress !== null ? `
                        <div class="loading-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${progress}%"></div>
                            </div>
                            <span id="progress-text">${progress}%</span>
                        </div>
                    ` : ''}
                </div>
            `;
            
            overlay.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        } else {
            if (overlay) {
                overlay.style.display = 'none';
                document.body.style.overflow = '';
            }
        }
    },

    /**
     * Update loading progress
     * @param {number} progress - Progress percentage (0-100)
     */
    updateProgress(progress) {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill && progressText) {
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `${progress}%`;
        }
    },

    /**
     * Scroll element into view smoothly
     * @param {HTMLElement} element - Element to scroll to
     * @param {string} behavior - Scroll behavior
     */
    scrollToElement(element, behavior = 'smooth') {
        element.scrollIntoView({ 
            behavior: behavior,
            block: 'start'
        });
    },

    /**
     * Format date for display
     * @param {Date} date - Date object
     * @returns {string} - Formatted date string
     */
    formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },

    /**
     * Animate number counting
     * @param {HTMLElement} element - Element to animate
     * @param {number} start - Start value
     * @param {number} end - End value
     * @param {number} duration - Animation duration in ms
     */
    animateCounter(element, start, end, duration = 1000) {
        const range = end - start;
        const increment = range / (duration / 50);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= end) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.round(current * 100) / 100;
        }, 50);
    }
};

/**
 * Medical utilities for health data processing
 */
const MedicalUtils = {
    /**
     * Get risk level based on prediction confidence
     * @param {number} confidence - Prediction confidence (0-1)
     * @param {string} prediction - Prediction result
     * @returns {object} - Risk level information
     */
    getRiskLevel(confidence, prediction) {
        // Normalize prediction format to handle both "No Tumor" and "no_tumor"
        const normalizedPrediction = prediction.toLowerCase().replace(/_/g, ' ');
        
        if (normalizedPrediction === 'no tumor') {
            return MEDICAL_CONFIG.RISK_LEVELS.NONE;
        }
        
        if (confidence >= MEDICAL_CONFIG.CONFIDENCE_THRESHOLDS.HIGH) {
            return MEDICAL_CONFIG.RISK_LEVELS.HIGH;
        } else if (confidence >= MEDICAL_CONFIG.CONFIDENCE_THRESHOLDS.MEDIUM) {
            return MEDICAL_CONFIG.RISK_LEVELS.MODERATE;
        } else {
            return MEDICAL_CONFIG.RISK_LEVELS.LOW;
        }
    },

    /**
     * Format confidence percentage
     * @param {number} confidence - Confidence value (0-1)
     * @returns {string} - Formatted percentage
     */
    formatConfidence(confidence) {
        return `${(confidence * 100).toFixed(1)}%`;
    },

    /**
     * Format prediction display
     * @param {string} prediction - Raw prediction from API
     * @returns {string} - Formatted prediction for display
     */
    formatPrediction(prediction) {
        // Convert underscored format to readable format
        return prediction.replace(/_/g, ' ')
                        .replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Get tumor type description
     * @param {string} tumorType - Type of tumor
     * @returns {string} - Description of tumor type
     */
    getTumorDescription(tumorType) {
        // Normalize the tumor type to handle different formats
        const normalizedType = tumorType.toLowerCase().replace(/_/g, ' ');
        
        const descriptions = {
            'no tumor': 'No abnormal growth detected in the brain tissue. The MRI scan appears normal.',
            'glioma': 'A type of tumor that occurs in the brain and spinal cord. Gliomas are a group of tumors that arise from glial cells.',
            'glioma_tumor': 'A type of tumor that occurs in the brain and spinal cord. Gliomas are a group of tumors that arise from glial cells.',
            'meningioma': 'A tumor that arises from the meninges, the protective membranes surrounding the brain and spinal cord.',
            'meningioma_tumor': 'A tumor that arises from the meninges, the protective membranes surrounding the brain and spinal cord.',
            'pituitary': 'A growth that develops in the pituitary gland at the base of the brain, which controls hormone production.',
            'pituitary_tumor': 'A growth that develops in the pituitary gland at the base of the brain, which controls hormone production.'
        };
        
        return descriptions[normalizedType] || `Analysis detected: ${tumorType.replace(/_/g, ' ')}. Please consult with a medical professional for detailed interpretation.`;
    },

    /**
     * Generate medical recommendations
     * @param {string} prediction - Prediction result
     * @param {number} confidence - Prediction confidence
     * @returns {string[]} - Array of recommendations
     */
    generateRecommendations(prediction, confidence) {
        const recommendations = [];
        
        // Normalize prediction format to handle both "No Tumor" and "no_tumor"
        const normalizedPrediction = prediction.toLowerCase().replace(/_/g, ' ');
        
        if (normalizedPrediction === 'no tumor') {
            recommendations.push('✅ No tumor detected - this is a positive result');
            recommendations.push('Continue regular health monitoring as recommended by your doctor');
            recommendations.push('Maintain a healthy lifestyle with proper nutrition and exercise');
            recommendations.push('Follow up with your healthcare provider as scheduled');
            if (confidence < MEDICAL_CONFIG.CONFIDENCE_THRESHOLDS.HIGH) {
                recommendations.push('Consider discussing this result with your doctor for confirmation');
            }
        } else {
            recommendations.push('⚠️ Consult with a neurologist immediately for proper evaluation');
            recommendations.push('Schedule additional imaging studies if recommended by your doctor');
            recommendations.push('Discuss treatment options with your medical team');
            recommendations.push('Bring these results to your next medical appointment');
            
            if (confidence < MEDICAL_CONFIG.CONFIDENCE_THRESHOLDS.MEDIUM) {
                recommendations.push('Consider seeking a second opinion due to lower confidence level');
            }
        }
        
        return recommendations;
    }
};

// Export utilities to global scope
window.FileUtils = FileUtils;
window.FormUtils = FormUtils;
window.APIUtils = APIUtils;
window.UIUtils = UIUtils;
window.MedicalUtils = MedicalUtils;