# pyrefly: ignore [missing-import]
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
from uuid import uuid4
import numpy as np
import os
import requests
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Dict
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

if "PORT" not in os.environ:
    os.environ["PORT"] = "10000"

# Import utility functions
from src.helpers.preprocessing import load_image_cv2, preprocess_image
from tensorflow.keras.models import load_model as tf_load_model
from src.modules.rag_chatbot import get_chatbot
from src.modules.report_generator import generate_report, generate_pdf_report

load_dotenv()

app = FastAPI(title="Brain Tumor Detection System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_model (1).h5" 
UPLOAD_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = [
    "glioma_tumor",
    "no_tumor", 
    "meningioma_tumor",
    "pituitary_tumor",
]
ALLOWED_FILE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024

# Global variables
_model = None
_chatbot = None
sessions: Dict[str, dict] = {}

# Pydantic models
class ChatMessage(BaseModel):
    session_id: str
    user_message: str

class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    bot_response: str

# Utility Functions
def get_model():
    global _model
    if _model is not None:
        return _model
    
    if not MODEL_PATH.exists():
        print(f"❌ FATAL ERROR: Model file not found at: {MODEL_PATH}")
        raise Exception(f"Model file not found: {MODEL_PATH}")
        
    try:
        print(f"Loading model from: {MODEL_PATH}")
        _model = tf_load_model(str(MODEL_PATH), compile=False, safe_mode=False)
        print(f"Model loaded successfully.")
        return _model
    except Exception as e:
        print(f"Error loading model: {e}")
        raise Exception(f"Failed to load model: {e}")

def get_or_initialize_chatbot():
    global _chatbot
    if _chatbot is not None:
        return _chatbot
    
    try:
        print("Loading chatbot knowledge base...")
        _chatbot = get_chatbot()
        print("✅ Chatbot knowledge base loaded successfully")
        return _chatbot
    except Exception as e:
        print(f"Error loading chatbot: {e}")
        raise Exception(f"Failed to load chatbot: {e}")

def prepare_image_for_prediction(image_path: Path) -> np.ndarray:
    print("Loading and preprocessing image...")
    loaded_image = load_image_cv2(image_path)
    batch = preprocess_image(loaded_image, target_size=(224, 224), normalize=True)
    print(f"Image preprocessed. Final shape: {batch.shape}")
    return batch

def download_model_from_google_drive():
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 100000000:  # 100MB minimum
        print("✅ Model file already exists")
        return True
    
    try:
        print(" Model file not found or corrupted. Downloading from Google Drive...")
        GOOGLE_DRIVE_FILE_ID = "1u-MzNhyYRNX4HrciMzHm-YIy-ci5snrY"
        
        MODEL_PATH.parent.mkdir(exist_ok=True)
        
        print(f"Downloading model from Google Drive...")
        
        # Use gdown for reliable large file downloads
        try:
            import gdown
        except ImportError:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
            import gdown
        
        # Download using gdown (handles large files and confirmations automatically)
        url = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}"
        gdown.download(url, str(MODEL_PATH), quiet=False)
        
        # Check if download was successful
        final_size = MODEL_PATH.stat().st_size
        if final_size > 100 * 1024 * 1024:  # Should be > 100MB
            print(f"Model downloaded successfully: {final_size / 1024 / 1024:.2f} MB")
            return True
        else:
            print(f"Downloaded file too small: {final_size / 1024 / 1024:.2f} MB")
            return False
            
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        print("Alternative: Manually download the model from Google Drive and place it in the models folder")
        return False

# API Routes
@app.get("/")
def root():
    return JSONResponse({
        "status": "active",
        "message": "Brain Tumor Detection API - Consolidated Server",
        "endpoints": {
            "prediction": "POST /prediction",
            "report": "GET /report/{filename}",
            "chat": "POST /chat"
        }
    })

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.get("/report/{filename}")
async def download_report(filename: str):
    """Download generated report PDF"""
    try:
        report_path = REPORTS_DIR / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        print(f" Serving report: {filename}")
        return FileResponse(
            path=str(report_path),
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f" Error serving report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report download failed: {str(e)}")

# PREDICTION ENDPOINT 

@app.post("/prediction")
async def predict(
    file: UploadFile = File(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    symptoms: str = Form(default="Not specified")
):

    try:
        # Validate file type
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Max is 10 MB.")

        # Save upload temporarily
        session_id = uuid4().hex
        ext = Path(file.filename).suffix or ".png"
        saved_path = UPLOAD_DIR / f"{session_id}{ext}"
        
        saved_path.write_bytes(contents)

        # Preprocess image
        batch = prepare_image_for_prediction(saved_path)

        # Load model and predict
        model = get_model()
        print(" Running model prediction...")
        preds = model.predict(batch)
        
        if preds.ndim != 2 or preds.shape[1] != len(CLASS_NAMES):
            raise RuntimeError(f"Unexpected prediction shape: {preds.shape}")

        pred_idx = int(np.argmax(preds[0]))
        pred_label = CLASS_NAMES[pred_idx]
        confidence = float(preds[0][pred_idx])

        print(f" Predicted: {pred_label} ({confidence:.4f})")

        # Prepare response data
        prediction_result = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "patient": {"name": name, "age": age, "gender": gender, "symptoms": symptoms},
            "filename": saved_path.name,
            "prediction": pred_label,
            "confidence": confidence,
            "probabilities": {CLASS_NAMES[i]: float(preds[0][i]) for i in range(len(CLASS_NAMES))},
        }

        # Generate AI report 
        patient_info_with_prediction = {
            "name": name, 
            "age": age, 
            "gender": gender, 
            "symptoms": symptoms,
            "prediction": pred_label,
            "confidence": confidence
        }
        
        # Use report generator 
        report_data = generate_report(pred_label, patient_info_with_prediction)
        
        # Generate PDF report 
        report_filename = f"report_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = generate_pdf_report(
            patient_info=patient_info_with_prediction,
            description=report_data.get('description', 'Analysis completed'),
            precautions=report_data.get('precautions', 'Consult healthcare professional'),
            things_to_remember=report_data.get('things_to_remember', 'Follow medical advice'),
            output_filename=report_filename
        )
        
        prediction_result["report_filename"] = report_filename
        prediction_result["report_content"] = f"Description: {report_data.get('description', '')}\n\nPrecautions: {report_data.get('precautions', '')}\n\nThings to Remember: {report_data.get('things_to_remember', '')}"
        
        print(f"Report generated: {report_filename}")
        return prediction_result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary file
        try:
            if saved_path.exists():
                saved_path.unlink()
        except Exception:
            pass

# CHAT ENDPOINT

@app.post("/chat")
async def chat(
    message: str = Form(...),
    session_id: str = Form(...)
):
    """Chat with AI assistant about brain tumor analysis"""
    try:
        # Initialize session if needed
        if session_id not in sessions:
            sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
        
        # Use pre-loaded chatbot instance
        chatbot = get_or_initialize_chatbot()
        
        # Generate response
        bot_response = chatbot.answer_question(message)
        
        # Store conversation
        sessions[session_id]["messages"].append({
            "user": message,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f" Chat response generated for session {session_id}")
        return ChatResponse(
            session_id=session_id,
            user_message=message,
            bot_response=bot_response
        )
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

#STARTUP & SHUTDOWN

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print(" BRAIN TUMOR DETECTION API - STARTING UP")
    print("="*50)
    
    try:
        # Download model from Google Drive if needed
        print(" Checking model availability...")
        model_ready = download_model_from_google_drive()
        
        if model_ready:
            # Pre-load AI model
            get_model()
            print("Model loaded successfully")
        else:
            print("Model not available - predictions will fail until model is configured")
        
        # Load the chatbot on the first chat request to keep startup memory low.
        print("Chatbot will be initialized on the first chat request")
        
        print("\nServer ready at http://localhost:8000")
        print(" Endpoints:")
        print("   - POST /prediction (MRI analysis)")
        print("   - GET /report/{filename} (Download report)")
        print("   - POST /chat (AI chatbot)")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"Startup error: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    print("\nServer shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
