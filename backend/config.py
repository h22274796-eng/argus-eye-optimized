import os
from pathlib import Path

class Settings:
    # Базовые пути
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_DIR = BASE_DIR.parent / "uploads"
    DB_PATH = str(BASE_DIR.parent / "argus_eye.db")
    
    # Путь к модели
    MODEL_PATH = str(BASE_DIR / "models" / "yolov8n.pt")
    
    # Настройки оптимизации (добавляем те, которых не хватало)
    USE_OPENVINO = True
    USE_SAHI = True
    CPU_THREADS = 4

settings = Settings()

# Создаем необходимые папки при старте
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(settings.MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)