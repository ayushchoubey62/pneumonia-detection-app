import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the trained MobileNetV2 model
model = load_model("pneumonia_mobilenetv2_finetuned.keras")

def predict_image(image_path):
    try:
        # Read and preprocess image
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))                     # Ensure model-compatible shape
        img = (img / 127.5) - 1.0                              # Normalize to [-1, 1]
        img = np.expand_dims(img, axis=0)

        # Predict
        pred = model.predict(img)[0][0]
        threshold = 0.6                                        # Custom best threshold
        label = "PNEUMONIA" if pred > threshold else "NORMAL"
        confidence = pred if label == "PNEUMONIA" else 1 - pred

        return label, round(confidence * 100, 2)
    except Exception as e:
        print("Prediction Error:", e)
        return "Error", 0.0
