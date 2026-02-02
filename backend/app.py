import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil
import logging
import os
from pathlib import Path
from exif import Image as ExifImage

# Импорты внутренних модулей
from backend.services.detector import OptimizedDetector
from backend.utils.change_detection import ChangeDetector
from backend.utils.database import db
from backend.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ArgusAPI")

app = FastAPI(
    title="Argus Eye API",
    description="API для детекции объектов и анализа изменений на снимках БПЛА"
)

# Настройка CORS для работы с Render и локальными фронтендами
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервисов
detector = OptimizedDetector()
change_detector = ChangeDetector()

def decimal_coords(coords, ref):
    """Преобразует координаты EXIF (градусы, минуты, секунды) в десятичный формат."""
    try:
        decimal = coords[0] + coords[1] / 60 + coords[2] / 3600
        if ref in ['S', 'W']:
            decimal = -decimal
        return float(decimal)
    except Exception:
        return None

def get_gps_coords(file_path):
    """Извлекает GPS координаты из метаданных изображения."""
    try:
        with open(file_path, 'rb') as f:
            img = ExifImage(f)
            if img.has_exif and hasattr(img, 'gps_latitude'):
                lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
                return lat, lon
    except Exception as e:
        logger.warning(f"Метаданные GPS не найдены в {file_path.name}: {e}")
    return None, None

@app.get("/api/v1/health")
async def health():
    """Проверка работоспособности API."""
    return {"status": "ok", "service": "Argus Eye", "online": True}

@app.post("/api/v1/detect")
async def detect(file: UploadFile = File(...)):
    """Эндпоинт для детекции объектов на изображении."""
    task_id = str(uuid.uuid4())
    extension = Path(file.filename).suffix or ".jpg"
    safe_name = f"{task_id}{extension}"
    file_path = settings.UPLOAD_DIR / safe_name
    
    # Сохранение файла на диск
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Ошибка сохранения файла: {e}")
        raise HTTPException(status_code=500, detail="Could not save image")

    # Извлечение координат
    lat, lon = get_gps_coords(file_path)
    
    try:
        # Запуск нейросети
        detections, proc_time = detector.run(str(file_path))
        
        # Сохранение задачи в SQLite
        db.save_detection_task({
            "task_id": task_id,
            "image_path": str(file_path),
            "detections_count": len(detections),
            "detections": detections,
            "processing_time": float(proc_time),
            "lat": lat,
            "lon": lon
        })

        return {
            "status": "success",
            "task_id": task_id, 
            "detections": detections, 
            "lat": lat, 
            "lon": lon,
            "metadata": {
                "filename": file.filename,
                "processing_time": round(proc_time, 2)
            }
        }
    except Exception as e:
        logger.error(f"Критическая ошибка детекции: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/tasks")
async def get_tasks():
    """Получение истории всех анализов."""
    try:
        return db.get_history()
    except Exception as e:
        logger.error(f"Ошибка БД: {e}")
        return []

@app.post("/api/v1/compare")
async def compare(
    file1: UploadFile = File(...), 
    file2: UploadFile = File(...), 
    method: str = Form("absdiff"), 
    threshold: int = Form(30)
):
    """Сравнение двух изображений для поиска изменений."""
    p1 = settings.UPLOAD_DIR / f"cmp1_{uuid.uuid4().hex}.png"
    p2 = settings.UPLOAD_DIR / f"cmp2_{uuid.uuid4().hex}.png"
    
    try:
        with p1.open("wb") as b1: shutil.copyfileobj(file1.file, b1)
        with p2.open("wb") as b2: shutil.copyfileobj(file2.file, b2)
        
        result = change_detector.compare(str(p1), str(p2), threshold=threshold, method=method)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Ошибка сравнения: {e}")
        return {"status": "error", "message": str(e)}

# Точка входа для запуска
if __name__ == "__main__":
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Запуск сервера на порту {port}...")
    
    # Запуск через uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False, # Отключаем reload в продакшене для стабильности
        log_level="info"
    )