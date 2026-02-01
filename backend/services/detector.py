import time
import cv2
import numpy as np
import torch
from pathlib import Path
from ultralytics import YOLO
from backend.config import settings

# Глобальное исправление безопасности Torch
import torch.serialization
original_load = torch.load
def safe_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False 
    return original_load(*args, **kwargs)
torch.load = safe_torch_load

# Исправленный импорт SAHI
try:
    from sahi.model import Yolov8DetectionModel
    from sahi.predict import get_sliced_prediction
    SAHI_AVAILABLE = True
except ImportError:
    SAHI_AVAILABLE = False

class OptimizedDetector:
    def __init__(self):
        print(f"⚙️ Инициализация модели: {settings.MODEL_PATH}")
        
        # Загружаем обычную модель (без OpenVINO, так как экспорт падает из-за прав доступа)
        try:
            self.model = YOLO(settings.MODEL_PATH)
        except:
            self.model = YOLO("yolov8n.pt")

        # Настройка SAHI с правильным классом
        self.sahi_model = None
        if SAHI_AVAILABLE and settings.USE_SAHI:
            try:
                self.sahi_model = Yolov8DetectionModel(
                    model_path=settings.MODEL_PATH,
                    confidence_threshold=0.25,
                    device='cpu'
                )
                print("✅ SAHI инициализирован корректно")
            except Exception as e:
                print(f"⚠️ Ошибка SAHI (используем обычный режим): {e}")

    def run(self, img_path, conf=0.25):
        start_time = time.time()
        img = cv2.imread(str(img_path))
        if img is None: return [], 0.0
            
        h, w = img.shape[:2]

        # Если SAHI доступен и картинка большая
        if self.sahi_model and settings.USE_SAHI and (h > 1080 or w > 1920):
            result = get_sliced_prediction(
                str(img_path),
                self.sahi_model,
                slice_height=512,
                slice_width=512,
                overlap_height_ratio=0.2,
                overlap_width_ratio=0.2
            )
            detections = [{"class": o.category.name, "conf": float(o.score.value), "bbox": o.bbox.to_xyxy()} 
                          for o in result.object_prediction_list]
        else:
            res = self.model(img, conf=conf)[0]
            detections = [{"class": self.model.names[int(b.cls)], "conf": float(b.conf), "bbox": b.xyxy[0].tolist()} 
                          for b in res.boxes]
        
        return detections, time.time() - start_time