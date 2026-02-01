from pathlib import Path
import time
from backend.models.model_manager import model_manager
from backend.utils.geo_utils import GeoReferencer
from backend.utils.database import db_instance  # Используем глобальный объект БД

class DetectionService:
    def __init__(self):
        self.model = None
        self.geo = GeoReferencer()

    async def process(self, image_path: Path, use_sahi=False):
        if self.model is None:
            self.model = model_manager.load_model()
        
        if self.model is None:
            return [], 0.0

        # Детекция объектов
        start_time = time.time()
        results = self.model(str(image_path), conf=0.25)[0]
        inference_time = time.time() - start_time
        
        detections = []
        for box in results.boxes:
            detections.append({
                "class_name": self.model.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist()
            })
            
        # Извлечение GPS координат из фото
        lat, lon = self.geo.get_coords(str(image_path))
        
        # Сохранение в базу данных (ВАЖНО для страницы "Карта")
        if db_instance:
            db_instance.save_task(
                task_id=image_path.stem.split('_')[0], # Берем UUID из имени файла
                image_path=image_path,
                detections=detections,
                lat=lat,
                lon=lon
            )
            
        return detections, inference_time