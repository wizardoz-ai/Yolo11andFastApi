from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ultralytics import YOLO
from PIL import Image
import io
import os

app = FastAPI()

# Modeli yükle
model = YOLO("model/yolo11x.pt")

# Çıktı dizini
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

class PredictionResponse(BaseModel):
    filename: str
    predictions: list

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Model çıkarımı
    results = model.predict(source=image, save=True, save_dir=output_dir)
    
    predictions = []
    for result in results:
        predictions.append({
            "class": result.boxes.cls.tolist(),
            "confidence": result.boxes.conf.tolist(),
            "coordinates": result.boxes.xyxy.tolist(),
        })

    return PredictionResponse(
        filename=file.filename,
        predictions=predictions
    )
