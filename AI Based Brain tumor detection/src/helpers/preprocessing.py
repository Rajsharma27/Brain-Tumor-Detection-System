from pathlib import Path
from typing import Tuple
import os
import numpy as np
import cv2

# Class labels
class_labels = ['glioma_tumor', 'no_tumor', 'meningioma_tumor', 'pituitary_tumor']

# Model input size
DEFAULT_SIZE: Tuple[int, int] = (224, 224)

def load_image_cv2(image_path: str | Path) -> np.ndarray:
    """
    Loads an image using cv2.
    Ensures the output is always a 3-channel BGR numpy array.
    Converts grayscale to BGR.
    """
    path = str(image_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"MRI image not found: {path}")

    image = cv2.imread(path)
    
    if image is None:
        raise IOError(f"Failed to load image (cv2.imread returned None): {path}")

    
    if image.ndim == 2 or (image.ndim == 3 and image.shape[2] == 1):
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
    return image


def preprocess_image(
    image: np.ndarray,  
    target_size: Tuple[int, int] = DEFAULT_SIZE,
    normalize: bool = True,  
) -> np.ndarray:
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    
    image_resized = cv2.resize(image_rgb, target_size, interpolation=cv2.INTER_LINEAR)

    
    array = image_resized.astype(np.float32)

    if normalize:
        array /= 255.0

    
    return np.expand_dims(array, axis=0)


