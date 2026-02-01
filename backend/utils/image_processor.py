"""
Обработка изображений с оптимизациями для CPU
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List, Union
import warnings
warnings.filterwarnings('ignore')

class ImageProcessor:
    """Класс для обработки изображений с оптимизациями"""
    
    def __init__(self, max_size: int = 1280):
        """
        Args:
            max_size: Максимальный размер изображения для обработки
        """
        self.max_size = max_size
        
        # Оптимизация OpenCV
        cv2.setNumThreads(2)  # Ограничиваем потоки для стабильности
    
    def load_image(self, image_path: Union[str, Path], optimize: bool = True) -> np.ndarray:
        """
        Загрузка изображения с оптимизацией
        
        Args:
            image_path: Путь к изображению
            optimize: Применять ли оптимизации
        
        Returns:
            np.ndarray: Загруженное изображение
        """
        # Загрузка изображения
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")
        
        # Конвертация цветового пространства (BGR -> RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if optimize:
            # Автоматический ресайз для оптимизации скорости
            image_rgb = self.auto_resize(image_rgb)
            
            # Улучшение качества для детекции
            image_rgb = self.enhance_for_detection(image_rgb)
        
        return image_rgb
    
    def auto_resize(self, image: np.ndarray) -> np.ndarray:
        """
        Автоматический ресайз изображения для оптимизации скорости
        
        Args:
            image: Исходное изображение
        
        Returns:
            np.ndarray: Ресайзнутое изображение
        """
        h, w = image.shape[:2]
        
        # Если изображение уже меньше максимального размера, оставляем как есть
        if max(h, w) <= self.max_size:
            return image
        
        # Вычисляем новые размеры с сохранением пропорций
        if h > w:
            new_h = self.max_size
            new_w = int(w * (self.max_size / h))
        else:
            new_w = self.max_size
            new_h = int(h * (self.max_size / w))
        
        # Ресайз с сохранением деталей
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        print(f"🔄 Авто-ресайз: {w}x{h} -> {new_w}x{new_h}")
        return resized
    
    def enhance_for_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Улучшение изображения для лучшей детекции объектов
        
        Args:
            image: Исходное изображение
        
        Returns:
            np.ndarray: Улучшенное изображение
        """
        # Конвертация в градации серого для некоторых операций
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Адаптивная гистограмма для улучшения контраста
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        
        # Преобразование обратно в RGB
        enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
        
        # Легкое увеличение резкости
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Смешивание с оригиналом для сохранения естественности
        alpha = 0.7
        result = cv2.addWeighted(image, alpha, sharpened, 1 - alpha, 0)
        
        return result
    
    def preprocess_for_yolo(self, image: np.ndarray, target_size: int = 640) -> np.ndarray:
        """
        Предобработка изображения для YOLO модели
        
        Args:
            image: Исходное изображение
            target_size: Целевой размер для YOLO
        
        Returns:
            np.ndarray: Предобработанное изображение
        """
        # Ресайз до целевого размера
        h, w = image.shape[:2]
        
        # Вычисляем размеры с сохранением пропорций и добавлением padding
        scale = min(target_size / h, target_size / w)
        new_h, new_w = int(h * scale), int(w * scale)
        
        # Ресайз изображения
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Добавление padding для получения квадратного изображения
        top = (target_size - new_h) // 2
        bottom = target_size - new_h - top
        left = (target_size - new_w) // 2
        right = target_size - new_w - left
        
        # Создание изображения с padding
        padded = cv2.copyMakeBorder(
            resized, top, bottom, left, right,
            cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )
        
        # Нормализация
        normalized = padded.astype(np.float32) / 255.0
        
        # Перестановка осей для YOLO (HWC -> CHW)
        if len(normalized.shape) == 3:
            normalized = np.transpose(normalized, (2, 0, 1))
        
        # Добавление batch dimension
        normalized = np.expand_dims(normalized, axis=0)
        
        return normalized
    
    def draw_detections(self, image: np.ndarray, detections: List[dict]) -> np.ndarray:
        """
        Отрисовка детекций на изображении
        
        Args:
            image: Исходное изображение
            detections: Список детекций
        
        Returns:
            np.ndarray: Изображение с отрисованными детекциями
        """
        result = image.copy()
        
        # Цвета для разных классов
        colors = {
            "person": (255, 0, 0),      # Красный
            "car": (0, 255, 0),        # Зеленый
            "truck": (0, 165, 255),    # Оранжевый
            "bus": (255, 0, 255),      # Фиолетовый
            "bicycle": (255, 255, 0),  # Голубой
            "motorcycle": (0, 255, 255) # Желтый
        }
        
        for detection in detections:
            bbox = detection.get("bbox", {})
            class_name = detection.get("class", "unknown")
            confidence = detection.get("confidence", 0)
            
            if not bbox:
                continue
            
            # Извлечение координат
            x = int(bbox.get("x", 0))
            y = int(bbox.get("y", 0))
            width = int(bbox.get("width", 0))
            height = int(bbox.get("height", 0))
            
            # Получение цвета для класса
            color = colors.get(class_name, (128, 128, 128))
            
            # Рисование bounding box
            cv2.rectangle(result, (x, y), (x + width, y + height), color, 2)
            
            # Создание текстовой метки
            label = f"{class_name}: {confidence:.2f}"
            
            # Вычисление размера текста
            font_scale = 0.5
            thickness = 1
            
            # Получение размеров текста
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
            )
            
            # Рисование фона для текста
            cv2.rectangle(
                result,
                (x, y - text_height - baseline - 5),
                (x + text_width, y),
                color,
                -1  # Заливка
            )
            
            # Рисование текста
            cv2.putText(
                result,
                label,
                (x, y - baseline - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),  # Белый текст
                thickness
            )
            
            # Если есть координаты GPS, добавляем иконку
            if "coordinates" in detection:
                # Рисование маленькой иконки локации
                icon_x = x + width - 20
                icon_y = y + 20
                cv2.circle(result, (icon_x, icon_y), 8, (0, 0, 255), -1)
                cv2.circle(result, (icon_x, icon_y), 5, (255, 255, 255), -1)
        
        return result
    
    def extract_frames_from_video(self, video_path: str, fps: int = 1) -> List[np.ndarray]:
        """
        Извлечение кадров из видео с оптимизацией для CPU
        
        Args:
            video_path: Путь к видео файлу
            fps: Количество кадров в секунду для извлечения
        
        Returns:
            List[np.ndarray]: Список извлеченных кадров
        """
        frames = []
        
        # Открытие видео файла
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Не удалось открыть видео файл: {video_path}")
        
        # Получение FPS видео
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(video_fps / fps) if fps > 0 else 1
        
        frame_count = 0
        success = True
        
        print(f"🎥 Извлечение кадров из видео (целевой FPS: {fps})...")
        
        while success:
            success, frame = cap.read()
            
            if not success:
                break
            
            # Извлекаем каждый N-й кадр
            if frame_count % frame_interval == 0:
                # Конвертация BGR -> RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Оптимизация размера
                frame_optimized = self.auto_resize(frame_rgb)
                
                frames.append(frame_optimized)
            
            frame_count += 1
        
        cap.release()
        
        print(f"✅ Извлечено {len(frames)} кадров из {frame_count} всего")
        return frames
    
    def save_image(self, image: np.ndarray, output_path: Union[str, Path], 
                   quality: int = 95) -> bool:
        """
        Сохранение изображения с оптимизацией
        
        Args:
            image: Изображение для сохранения
            output_path: Путь для сохранения
            quality: Качество JPEG (1-100)
        
        Returns:
            bool: Успешно ли сохранение
        """
        try:
            # Конвертация RGB -> BGR для OpenCV
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
            
            # Сохранение с указанным качеством
            success = cv2.imwrite(str(output_path), image_bgr, 
                                 [cv2.IMWRITE_JPEG_QUALITY, quality])
            
            if success:
                print(f"💾 Изображение сохранено: {output_path}")
            else:
                print(f"❌ Не удалось сохранить изображение: {output_path}")
            
            return success
            
        except Exception as e:
            print(f"❌ Ошибка сохранения изображения: {e}")
            return False
    
    def create_mosaic(self, images: List[np.ndarray], grid_size: Tuple[int, int] = (2, 2)) -> np.ndarray:
        """
        Создание мозаики из нескольких изображений
        
        Args:
            images: Список изображений
            grid_size: Размер сетки (строки, колонки)
        
        Returns:
            np.ndarray: Мозаичное изображение
        """
        if not images:
            raise ValueError("Список изображений пуст")
        
        rows, cols = grid_size
        max_images = rows * cols
        images_to_use = images[:max_images]
        
        # Ресайз всех изображений до одного размера
        target_h, target_w = 300, 400  # Размер каждого изображения в мозаике
        
        resized_images = []
        for img in images_to_use:
            resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
            resized_images.append(resized)
        
        # Создание мозаики
        mosaic_rows = []
        for i in range(rows):
            row_images = resized_images[i*cols:(i+1)*cols]
            
            # Если в строке не хватает изображений, добавляем пустые
            while len(row_images) < cols:
                row_images.append(np.zeros((target_h, target_w, 3), dtype=np.uint8))
            
            # Объединение изображений в строку
            row = np.hstack(row_images)
            mosaic_rows.append(row)
        
        # Объединение строк
        mosaic = np.vstack(mosaic_rows)
        
        return mosaic

# Создание глобального экземпляра процессора изображений
image_processor = ImageProcessor()