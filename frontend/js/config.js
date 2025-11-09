// Backend integration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        HEALTH: '/health',
        PREDICTION: '/prediction',
        CHAT: '/chat',
        REPORT: '/report'
    },
    TIMEOUT: 30000, 
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000 
};

// UI Configuration
const UI_CONFIG = {
    MAX_FILE_SIZE: 10 * 1024 * 1024, 
    ALLOWED_FILE_TYPES: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/tiff'],
    TOAST_DURATION: 5000,
    TYPING_INDICATOR_DELAY: 1000,
    PROGRESS_UPDATE_INTERVAL: 100,
    CHAT_SCROLL_BEHAVIOR: 'smooth'
};

// Medical Categories Configuration
const MEDICAL_CONFIG = {
    TUMOR_TYPES: [
        'No Tumor',
        'Glioma',
        'Meningioma', 
        'Pituitary'
    ],
    CONFIDENCE_THRESHOLDS: {
        HIGH: 0.8,
        MEDIUM: 0.6,
        LOW: 0.4
    },
    RISK_LEVELS: {
        NONE: { color: '#10b981', label: 'No Risk' },
        LOW: { color: '#10b981', label: 'Low Risk' },
        MODERATE: { color: '#f59e0b', label: 'Moderate Risk' },
        HIGH: { color: '#ef4444', label: 'High Risk' },
        CRITICAL: { color: '#dc2626', label: 'Critical' }
    }
};

// Export configuration
window.API_CONFIG = API_CONFIG;
window.UI_CONFIG = UI_CONFIG;
window.MEDICAL_CONFIG = MEDICAL_CONFIG;