# 🧠 BrainScan AI - AI-Based Brain Tumor Detection System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-orange.svg)](https://www.tensorflow.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An advanced AI-powered medical imaging system for automated brain tumor detection and classification. This comprehensive solution combines deep learning, RAG-based chatbot assistance, and automated medical report generation to aid healthcare professionals in brain tumor diagnosis.

## 🌟 Key Features

- **🎯 Multi-Class Tumor Detection**: Classifies brain MRI scans into 4 categories:
  - Glioma Tumor
  - Meningioma Tumor
  - Pituitary Tumor
  - No Tumor

- **🤖 Intelligent RAG Chatbot**: Context-aware medical assistant powered by:
  - LangChain for conversational AI
  - FAISS vector database for knowledge retrieval
  - Google Gemini 2.0 for natural language understanding
  - PDF-based medical knowledge base

- **📄 Automated Report Generation**: 
  - AI-generated comprehensive medical reports
  - Professional PDF formatting with patient information
  - Detailed analysis and recommendations

- **💻 Modern User Interface**:
  - Interactive Streamlit web application
  - Real-time prediction visualization
  - Confidence score display
  - Patient data management

- **🔧 Production-Ready Backend**:
  - FastAPI REST API
  - Async request handling
  - CORS support for cross-origin requests
  - Docker containerization support

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Model Information](#model-information)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│              (User Interface & Visualization)                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                     │
│  ┌──────────────┬──────────────┬─────────────────────────┐  │
│  │ Prediction   │   Chatbot    │  Report Generator       │  │
│  │   Service    │   Service    │      Service            │  │
│  └──────────────┴──────────────┴─────────────────────────┘  │
└────────────────────┬───────────────┬──────────────┬─────────┘
                     │               │              │
         ┌───────────┼───────────────┼──────────────┼──────┐
         ↓           ↓               ↓              ↓      ↓
    ┌────────┐  ┌────────┐    ┌─────────┐    ┌────────┐  ┌────────┐
    │TensorFlow│ │FAISS   │    │ Google  │    │SQLite  │  │ File   │
    │  Model  │  │Vector  │    │ Gemini  │    │Database│  │Storage │
    │   (.h5) │  │  DB    │    │   API   │    │        │  │        │
    └────────┘  └────────┘    └─────────┘    └────────┘  └────────┘
```

## 🔧 Prerequisites

- **Python**: 3.10 or higher
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 2GB free space
- **OS**: Windows, Linux, or macOS
- **GPU** (Optional): CUDA-compatible GPU for faster inference

### Required API Keys

- **Google API Key**: For Gemini AI (report generation and chatbot)
  - Get it from: [Google AI Studio](https://makersuite.google.com/app/apikey)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/brain-tumor-detection.git
cd brain-tumor-detection
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download Model Weights

Place your trained model file (`best_model (1).h5`) in the `models/` directory:

```
models/
  └── best_model (1).h5
```

### 5. Prepare Knowledge Base (Optional)

Add medical PDF documents to the `Data/` directory for the RAG chatbot:

```
Data/
  ├── medical_reference_1.pdf
  ├── medical_reference_2.pdf
  └── ...
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE-API-KEY=your_google_api_key_here

# Optional: Database Configuration
DATABASE_URL=sqlite:///./brain_tumor_app.db

# Optional: Model Configuration
MODEL_PATH=models/best_model (1).h5
```

### 2. Configuration Files

The `config.py` file contains TensorFlow and warning suppressions. Modify if needed for your environment.

## 🚀 Usage

### Starting the Application

#### Option 1: Run Both Services (Recommended)

**Terminal 1 - Backend API:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend UI:**
```bash
streamlit run app.py
```

The application will be available at:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

#### Option 2: Backend Only

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Access the interactive API documentation at: http://localhost:8000/docs

### Using the Application

1. **Patient Information**
   - Enter patient name, age, and gender
   - Add symptoms and medical history

2. **Upload MRI Scan**
   - Support formats: JPEG, PNG, TIFF
   - Maximum file size: 10MB

3. **Get Prediction**
   - Click "Analyze MRI Scan"
   - View tumor classification results
   - See confidence scores

4. **Generate Report**
   - Automatic AI-generated medical report
   - Download as PDF

5. **Chat with AI Assistant**
   - Ask questions about diagnosis
   - Get context-aware medical information
   - Discuss treatment options

## 📚 API Documentation

### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-22T10:30:00"
}
```

### Prediction Endpoint

```http
POST /prediction
```

**Request:**
- `file`: MRI scan image (multipart/form-data)
- `name`: Patient name (form field)
- `age`: Patient age (form field)
- `gender`: Patient gender (form field)
- `symptoms`: Patient symptoms (form field)

**Response:**
```json
{
  "predicted_class": "glioma_tumor",
  "confidence": 0.95,
  "all_predictions": {
    "glioma_tumor": 0.95,
    "meningioma_tumor": 0.03,
    "pituitary_tumor": 0.01,
    "no_tumor": 0.01
  },
  "patient_info": {
    "name": "John Doe",
    "age": 45,
    "gender": "Male",
    "symptoms": "Headache, vision problems"
  },
  "prediction_id": "uuid-here",
  "timestamp": "2025-12-22T10:30:00"
}
```

### Chatbot Endpoint

```http
POST /chat
```

**Request:**
```json
{
  "session_id": "session-uuid",
  "user_message": "What is glioma?"
}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "user_message": "What is glioma?",
  "bot_response": "Glioma is a type of tumor that occurs in the brain..."
}
```

### Report Generation Endpoint

```http
POST /generate-report
```

**Request:**
```json
{
  "prediction": "glioma_tumor",
  "confidence": 0.95,
  "patient_name": "John Doe",
  "patient_age": 45,
  "patient_gender": "Male",
  "symptoms": "Headache, vision problems"
}
```

**Response:**
```json
{
  "report_id": "report-uuid",
  "report_path": "/reports/report-uuid.pdf",
  "download_url": "/download-report/report-uuid"
}
```

### Download Report

```http
GET /download-report/{report_id}
```

Returns PDF file for download.

## 📁 Project Structure

```
brain-tumor-detection/
│
├── app.py                      # Streamlit frontend application
├── main.py                     # FastAPI backend server
├── config.py                   # Configuration and environment setup
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── README.md                   # Project documentation
│
├── models/                     # ML model storage
│   └── best_model (1).h5      # Trained TensorFlow/Keras model
│
├── Data/                       # Knowledge base for RAG chatbot
│   └── *.pdf                  # Medical reference documents
│
├── src/                        # Source code modules
│   ├── database/              # Database models and operations
│   │   ├── db_model.py        # SQLAlchemy models
│   │   ├── patient_data.py    # Patient data management
│   │   └── user_database.py   # User authentication
│   │
│   ├── helpers/               # Utility functions
│   │   ├── __init__.py
│   │   └── preprocessing.py   # Image preprocessing utilities
│   │
│   └── modules/               # Core application modules
│       ├── chatbot_service.py    # Chatbot service wrapper
│       ├── prompt_generator.py   # AI prompt engineering
│       ├── rag_chatbot.py        # RAG chatbot implementation
│       └── report_generator.py   # Report generation logic
│
├── utilis/                    # Additional utilities
│   └── predict.py            # Prediction helper functions
│
├── uploads/                   # Temporary upload storage
├── reports/                   # Generated PDF reports
└── public/                    # Static assets
```

## 🧪 Model Information

### Architecture
- **Base Model**: Convolutional Neural Network (CNN)
- **Framework**: TensorFlow/Keras
- **Input Shape**: 224x224x3 (RGB images)
- **Output Classes**: 4 (Glioma, Meningioma, Pituitary, No Tumor)

### Training Details
- **Dataset**: Brain MRI Images
- **Preprocessing**: 
  - Resizing to 224x224
  - Normalization (0-1 range)
  - Augmentation techniques applied

### Performance Metrics
- **Accuracy**: Varies by model training
- **Inference Time**: <1 second per image
- **Model Size**: ~100MB

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t brain-tumor-detection .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/reports:/app/reports \
  --name brain-tumor-api \
  brain-tumor-detection
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./models:/app/models
      - ./uploads:/app/uploads
      - ./reports:/app/reports
      - ./Data:/app/Data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## 🔒 Security Considerations

- **Patient Data**: All patient information is handled securely
- **API Keys**: Never commit API keys to version control
- **File Uploads**: Validated for type and size
- **Session Management**: Unique session IDs for each user
- **CORS**: Configure allowed origins in production

## 🛠️ Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Code Formatting

```bash
# Install formatters
pip install black flake8 isort

# Format code
black .
isort .
flake8 .
```

## 📊 Performance Optimization

- **Model Caching**: Model loaded once and reused
- **Vector Store Caching**: FAISS index cached in memory
- **Async Processing**: FastAPI async endpoints
- **Image Preprocessing**: Optimized OpenCV operations

## 🐛 Troubleshooting

### Common Issues

**Issue**: Backend not starting
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process or use different port
uvicorn main:app --port 8001
```

**Issue**: Model file not found
- Ensure `best_model (1).h5` is in the `models/` directory
- Check file permissions

**Issue**: API key errors
- Verify `.env` file exists and contains valid keys
- Check environment variable names match

**Issue**: Memory errors
- Reduce batch size for predictions
- Close other applications
- Consider using GPU

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- TensorFlow team for the deep learning framework
- LangChain for RAG capabilities
- Google for Gemini AI API
- Streamlit for the amazing UI framework
- FastAPI for the modern web framework
- Medical community for knowledge base resources

## 📞 Contact

For questions, suggestions, or issues:

- **Email**: your.email@example.com
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/brain-tumor-detection/issues)
- **LinkedIn**: [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 📈 Roadmap

- [ ] Multi-language support
- [ ] Enhanced model with attention mechanisms
- [ ] Real-time collaboration features
- [ ] Mobile application
- [ ] Integration with DICOM viewers
- [ ] Advanced analytics dashboard
- [ ] Batch processing capabilities
- [ ] User authentication and authorization

## ⚠️ Disclaimer

**IMPORTANT**: This software is intended for research and educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions regarding medical conditions.

---

Made with ❤️ for advancing healthcare through AI
