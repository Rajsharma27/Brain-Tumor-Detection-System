# 🧠 Brain Tumor Detection System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-orange?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> 🎯 **AI-powered brain tumor detection system using VGG16 architecture for MRI analysis with automated report generation.**

---

## 📋 Table of Contents

- [🚀 Features](#-features)
- [💻 Tech Stack](#-tech-stack)
- [🎯 Tumor Classification](#-tumor-classification)
- [⚡ Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [📊 Usage](#-usage)
- [🌐 API Endpoints](#-api-endpoints)
- [📄 License](#-license)

---

## 🚀 Features

- **🧠 VGG16 Model**: Deep learning classification using pre-trained VGG16 architecture
- **🔬 Multi-Class Classification**: Detects 4 types of brain conditions (Glioma, Meningioma, Pituitary, No Tumor)
- **⚡ Real-Time Analysis**: Instant MRI scan processing and results
- **📊 AI-Generated Reports**: Medical reports with recommendations using local LLM
- **🤖 RAG Chatbot**: Medical Q&A assistant powered by knowledge base
- **📱 Streamlit Interface**: Interactive web application
- **🔌 RESTful API**: FastAPI backend
- **📄 PDF Generation**: Professional medical report downloads

---

## 💻 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python 3.8+, FastAPI, TensorFlow 2.15.0 |
| **Frontend** | Streamlit |
| **AI/ML** | VGG16 (TensorFlow/Keras), OpenCV, Ollama LLM, RAG Chatbot, Knowledge Base |
| **Data Processing** | Pillow, ReportLab (PDF) |

---

## 🎯 Tumor Classification

### 🧬 Supported Classifications

| Class | Description | Characteristics |
|-------|-------------|-----------------|
| **🔴 Glioma Tumor** | Brain/spinal cord tumor | Aggressive, requires immediate attention |
| **🟢 No Tumor** | Healthy brain tissue | Normal brain scan, no abnormalities |
| **🟡 Meningioma Tumor** | Membrane tumor | Usually benign, slow-growing |
| **🔵 Pituitary Tumor** | Pituitary gland tumor | Hormone-related, treatable |

### 🤖 Model Information
- **Architecture**: VGG16 Convolutional Neural Network
- **Framework**: TensorFlow/Keras
- **Input Size**: 224x224x3 RGB images
- **Output**: 4-class classification

---

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/Rajsharma27/Brain-Tumor-Detection-System.git
cd Brain-Tumor-Detection-System

# Install dependencies
pip install -r "AI Based Brain tumor detection/requirements.txt"

# Setup local LLM (optional)
ollama pull gemma2:2b

# Start the system
cd "AI Based Brain tumor detection"
python main.py
```

**Access Points:**
- 🌍 **Streamlit App**: http://localhost:8501  
- ⚡ **API Docs**: http://localhost:8000/docs
- 📊 **Health Check**: http://localhost:8000/health

---

## 📦 Installation

### Step-by-Step Setup

1. **Clone & Navigate**
```bash
git clone https://github.com/Rajsharma27/Brain-Tumor-Detection-System.git
cd Brain-Tumor-Detection-System
```

2. **Create Virtual Environment**
```bash
python -m venv brain_tumor_env
# Windows: brain_tumor_env\Scripts\activate
# Linux/macOS: source brain_tumor_env/bin/activate
```

3. **Install Dependencies**
```bash
cd "AI Based Brain tumor detection"
pip install -r requirements.txt
```

4. **Setup Local LLM (Optional)**
```bash
# Install Ollama: https://ollama.ai
ollama serve
ollama pull gemma2:2b
```

5. **Start Application**
```bash
# Start Streamlit App (includes backend)
python main.py
```

---

## 📊 Usage

### 🖥️ Streamlit Interface
1. Open browser → `http://localhost:8501`
2. Upload MRI scan (PNG, JPG, TIFF)
3. Fill patient details
4. Click "Analyze Brain Scan"
5. View results and download PDF report
6. Use chatbot for medical questions

### 🔌 API Usage

**Prediction:**
```python
import requests

url = "http://localhost:8000/prediction"
files = {"file": open("brain_scan.jpg", "rb")}
data = {"name": "John Doe", "age": 45, "gender": "male"}

response = requests.post(url, files=files, data=data)
result = response.json()
print(f"Prediction: {result['prediction']}")
```

**Chatbot:**
```python
url = "http://localhost:8000/chat"
data = {"message": "What are brain tumor symptoms?", "session_id": "user123"}
response = requests.post(url, data=data)
print(response.json()["bot_response"])
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/prediction` | Analyze brain MRI scan |
| `GET` | `/report/{filename}` | Download PDF report |
| `POST` | `/chat` | Chat with AI assistant |
| `GET` | `/health` | System health check |

### Example Response
```json
{
  "prediction": "meningioma_tumor",
  "confidence": 0.9759,
  "report_filename": "report_abc123.pdf",
  "probabilities": {
    "glioma_tumor": 0.0123,
    "no_tumor": 0.0089,
    "meningioma_tumor": 0.9759,
    "pituitary_tumor": 0.0029
  }
}
```

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgments

- **🧠 TensorFlow Team**: For the deep learning framework
- **⚡ FastAPI**: For the web framework  
- **🤖 Gemini**: For chatbot and report generation
- **🎨 Streamlit**: For the interactive web interface

---


