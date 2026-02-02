import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil
import logging
import os
from pathlib import Path
from exif import Image as ExifImage

from backend.services.detector import OptimizedDetector
from backend.utils.change_detection import ChangeDetector
from backend.utils.database import db
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ArgusAPI")

app = FastAPI(title="Argus Eye API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = OptimizedDetector()
change_detector = ChangeDetector()

def decimal_coords(coords, ref):
    try:
        decimal = coords[0] + coords[1] / 60 + coords[2] / 3600
        if ref in ['S', 'W']: decimal = -decimal
        return float(decimal)
    except: return None

def get_gps_coords(file_path):
    try:
        with open(file_path, 'rb') as f:
            img = ExifImage(f)
            if img.has_exif and hasattr(img, 'gps_latitude'):
                lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
                return lat, lon
    except: pass
    return None, None

@app.post("/api/v1/detect")
async def detect(file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    extension = Path(file.filename).suffix or ".png"
    file_path = settings.UPLOAD_DIR / f"{task_id}{extension}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    lat, lon = get_gps_coords(file_path)
    
    try:
        detections, proc_time = detector.run(str(file_path))
        db.save_detection_task({
            "task_id": task_id,
            "image_path": str(file_path),
            "detections_count": len(detections),
            "detections": detections,
            "processing_time": float(proc_time),
            "lat": lat,
            "lon": lon
        })
        return {"task_id": task_id, "detections": detections, "lat": lat, "lon": lon, "status": "success"}
    except Exception as e:
        logger.error(f"Ошибка детекции: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/health")
async def health(): return {"status": "ok"}

@app.get("/api/v1/tasks")
async def get_tasks(): return db.get_history()

@app.post("/api/v1/compare")
async def compare(file1: UploadFile = File(...), file2: UploadFile = File(...), method: str = Form("absdiff"), threshold: int = Form(30)):
    p1 = settings.UPLOAD_DIR / f"cmp1_{uuid.uuid4().hex}.png"
    p2 = settings.UPLOAD_DIR / f"cmp2_{uuid.uuid4().hex}.png"
    with p1.open("wb") as b1: shutil.copyfileobj(file1.file, b1)
    with p2.open("wb") as b2: shutil.copyfileobj(file2.file, b2)
    result = change_detector.compare(str(p1), str(p2), threshold=threshold, method=method)
    return {"status": "success", "result": result}

if __name__ == "__main__":
    # Render передает PORT в переменную окружения
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)