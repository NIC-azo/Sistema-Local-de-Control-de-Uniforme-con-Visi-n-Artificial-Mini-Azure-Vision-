import cv2
import numpy as np
import base64
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ultralytics import YOLO

from core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Sistema Local de Inspección Visual - Detección de Corbata",
    description="Pipeline local de inferencia, privacidad facial y métricas LAN",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Carga de Modelos
# 1. Modelo base para detectar si hay una persona en cámara (Fase 2 - Endpoint 1)
model_persona = YOLO("yolov8n.pt")
# 2. Modelo entrenado por ti para evaluar el uniforme (Fase 2 - Endpoint 2)
model_uniforme = YOLO(settings.MODEL_PATH)

class FramePayload(BaseModel):
    image: str 
    client_timestamp: Optional[float] = 0.0

def decode_base64_image(base64_string: str):
    encoded_data = base64_string.split(',')[1] if ',' in base64_string else base64_string
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

@app.post("/vision/general")
async def check_person(payload: FramePayload):
    img = decode_base64_image(payload.image)
    
    # Inferencia con modelo base YOLOv8
    results = model_persona(img)
    persona_detectada = False
    
    # YOLOv8 retorna las clases detectadas. La clase '0' en COCO es 'person'.
    for box in results[0].boxes:
        if int(box.cls[0]) == 0:
            persona_detectada = True
            break
            
    return {"persona_detectada": persona_detectada}

@app.post("/vision/uniforme")
async def check_uniform(payload: FramePayload):
    img = decode_base64_image(payload.image)
    
    # Inferencia con tu modelo entrenado
    results = model_uniforme(img)
    top_class_idx = results[0].probs.top1
    confianza = float(results[0].probs.top1conf)
    clase_predicha = results[0].names[top_class_idx]
    
    acceso = "DENEGADO"
    if clase_predicha == "con_corbata" and confianza >= settings.CONFIDENCE_THRESHOLD:
        acceso = "PERMITIDO"
    else:
        # Si es menor a 80% o es otra clase, forzamos la salida a "sin_corbata"
        clase_predicha = "sin_corbata"
        
    return {
        "estado": clase_predicha,
        "confianza": round(confianza, 2),
        "acceso": acceso
    }