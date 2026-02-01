import os
from pathlib import Path
from ultralytics import YOLO

class ModelManager:
    def __init__(self, model_name="yolov8n.pt"):
        # Определяем путь: папка проекта / backend / models
        self.models_dir = Path(__file__).parent.resolve()
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.models_dir / model_name
        self.model = None

    def load_model(self):
        """Загружает модель. Если файла нет, YOLO скачает его автоматически."""
        try:
            if not self.model_path.exists():
                print(f"📥 Модель не найдена. Начинаю загрузку {self.model_name}...")
                # При указании только имени 'yolov8n.pt', библиотека скачает её в текущую директорию
                # а затем мы её переместим или сохраним по нужному пути.
                self.model = YOLO("yolov8n.pt") 
                self.model.save(str(self.model_path))
                print(f"✅ Модель сохранена в: {self.model_path}")
            else:
                self.model = YOLO(str(self.model_path))
            
            return self.model
        except Exception as e:
            print(f"❌ Критическая ошибка при загрузке модели: {e}")
            return None

model_manager = ModelManager()