from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import numpy as np
import uvicorn
import os 


from src.helpers.preprocessing import load_image_cv2, preprocess_image
from tensorflow.keras.models import load_model as tf_load_model

app = FastAPI(title="Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent


MODEL_PATH = BASE_DIR / "models" / "best_model (1).h5" 

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


CLASS_NAMES = [
    "glioma_tumor",
    "no_tumor",
    "meningioma_tumor",
    "pituitary_tumor",
]

ALLOWED_FILE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  

_model = None

def get_model():
    global _model
    if _model is not None:
        return _model
    
    if not MODEL_PATH.exists():
        print(f" FATAL ERROR: Model file not found at: {MODEL_PATH}")
        raise Exception(f"Model file not found: {MODEL_PATH}")
        
    try:
        print(f" Loading model from: {MODEL_PATH}")
        _model = tf_load_model(str(MODEL_PATH), compile=False, safe_mode=False)
        print(f"✅ Model loaded successfully. Input shape: {_model.input_shape}")
        return _model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise Exception(f"Failed to load model: {e}")

def prepare_image_for_prediction(image_path: Path) -> np.ndarray:
    
    print("🔄 Loading and preprocessing image...")
    loaded_image = load_image_cv2(image_path)
    
    # Preprocess to 224x224, RGB, and normalize
    batch = preprocess_image(loaded_image, target_size=(224, 224), normalize=True)
    
    print(f"📊 Image preprocessed. Final shape: {batch.shape}")
    return batch

@app.get("/")
async def root():
    return {"message": "Prediction API is running", "model_path": str(MODEL_PATH)}

@app.get("/health")
async def health():
    
    return {
        "status": "ok",
        "model_exists": MODEL_PATH.exists(),
        "expected_input": {"height": 224, "width": 224, "channels": 3},
        "upload_dir": str(UPLOAD_DIR),
    }

@app.post("/predict")
async def predict(
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    symptoms: str = Form(default=""),
    file: UploadFile = File(...),
):
    
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max is 10 MB.")

    # Save upload
    session_id = uuid4().hex
    ext = Path(file.filename).suffix or ".png"
    saved_path = UPLOAD_DIR / f"{session_id}{ext}"
    
    try:
        saved_path.write_bytes(contents)

        # Preprocess
        batch = prepare_image_for_prediction(saved_path)

        # Load model (full .keras)
        model = get_model()

        # Predict
        print("🧠 Running model prediction...")
        preds = model.predict(batch)
        
        if preds.ndim != 2 or preds.shape[1] != len(CLASS_NAMES):
            raise RuntimeError(f"Unexpected prediction shape: {preds.shape}. Check CLASS_NAMES.")

        pred_idx = int(np.argmax(preds[0]))
        pred_label = CLASS_NAMES[pred_idx]
        confidence = float(preds[0][pred_idx])

        print(f"📈 Prediction values: {preds.tolist()}")
        print(f"✅ Predicted: {pred_label} ({confidence:.4f})")

        return {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "patient": {"name": name, "age": age, "gender": gender, "symptoms": symptoms},
            "filename": saved_path.name,
            "prediction": pred_label,
            "confidence": confidence,
            "probabilities": {CLASS_NAMES[i]: float(preds[0][i]) for i in range(len(CLASS_NAMES))},
        }
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            if os.path.exists(saved_path):
                os.remove(saved_path)
            await file.close()
        except Exception:
            pass 

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)