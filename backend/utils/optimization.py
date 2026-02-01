"""
Оптимизации производительности для CPU

Содержит методы для ускорения обработки на обычных ноутбуках
без GPU.
"""

import os
import gc
import psutil
import threading
from typing import Optional, Callable
import numpy as np
import cv2

class CPUOptimizer:
    """Оптимизатор производительности для CPU"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.original_threads = cv2.getNumThreads()
        
    def optimize_system(self):
        """Применение системных оптимизаций"""
        print("⚡ Применение CPU оптимизаций...")
        
        # Оптимизация OpenCV
        cv2.setNumThreads(2)  # Ограничиваем потоки OpenCV
        os.environ['OMP_NUM_THREADS'] = '2'
        os.environ['MKL_NUM_THREADS'] = '2'
        
        # Настройка приоритета процесса (Linux/Mac)
        if hasattr(os, 'nice'):
            try:
                os.nice(10)  # Понижаем приоритет для стабильности
            except:
                pass
        
        print(f"✅ OpenCV threads: {cv2.getNumThreads()} (было {self.original_threads})")
    
    def memory_optimization(self, model=None):
        """Оптимизация использования памяти"""
        print("🧹 Оптимизация памяти...")
        
        # Принудительная сборка мусора
        gc.collect()
        
        # Очистка кэшей NumPy
        try:
            import numpy as np
            np._globals._clear()  # type: ignore
        except:
            pass
        
        # Оптимизация модели если есть
        if model is not None:
            if hasattr(model, 'model'):
                try:
                    model.model.eval()  # Режим инференса
                    model.model.to('cpu')
                    model.model.share_memory()  # Разделяемая память
                except:
                    pass
        
        # Статистика памяти
        memory_info = self.process.memory_info()
        print(f"📊 Использование памяти: {memory_info.rss / 1024 / 1024:.1f} MB")
    
    def batch_processing_optimization(self, images: list, batch_size: int = 4):
        """
        Оптимизация пакетной обработки изображений
        
        Args:
            images: Список изображений для обработки
            batch_size: Размер пакета (оптимально 2-4 для CPU)
        
        Returns:
            list: Пакеты изображений
        """
        # Автоматический подбор размера пакета на основе памяти
        available_memory = psutil.virtual_memory().available / 1024 / 1024  # MB
        
        if available_memory < 1000:  # < 1GB
            batch_size = 2
        elif available_memory < 2000:  # < 2GB
            batch_size = 3
        else:
            batch_size = min(batch_size, 4)
        
        # Создание пакетов
        batches = [images[i:i + batch_size] for i in range(0, len(images), batch_size)]
        print(f"📦 Пакетная обработка: {len(images)} изображений → {len(batches)} пакетов по {batch_size}")
        
        return batches
    
    def resize_for_speed(self, image: np.ndarray, max_dimension: int = 1280) -> np.ndarray:
        """
        Ресайз изображения для ускорения обработки с сохранением качества
        
        Args:
            image: Исходное изображение
            max_dimension: Максимальный размер по любой стороне
        
        Returns:
            np.ndarray: Ресайзнутое изображение
        """
        h, w = image.shape[:2]
        
        # Если изображение уже меньше максимального размера, оставляем как есть
        if max(h, w) <= max_dimension:
            return image
        
        # Вычисляем новые размеры с сохранением пропорций
        if h > w:
            new_h = max_dimension
            new_w = int(w * (max_dimension / h))
        else:
            new_w = max_dimension
            new_h = int(h * (max_dimension / w))
        
        # Ресайз с интерполяцией для сохранения деталей
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        print(f"🔄 Ресайз изображения: {w}x{h} → {new_w}x{new_h}")
        return resized
    
    def enable_tf32_if_available(self):
        """Включение TF32 если доступно (ускорение на некоторых CPU)"""
        try:
            import torch
            if hasattr(torch, 'set_float32_matmul_precision'):
                torch.set_float32_matmul_precision('high')
                print("✅ Включена TF32 поддержка")
        except:
            pass
    
    def monitor_performance(self, func: Callable, *args, **kwargs):
        """
        Мониторинг производительности функции
        
        Args:
            func: Функция для мониторинга
            *args, **kwargs: Аргументы функции
        
        Returns:
            Результат выполнения функции и метрики производительности
        """
        import time
        
        # Замер использования памяти до выполнения
        memory_before = psutil.virtual_memory().used
        
        # Замер времени выполнения
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            end_time = time.time()
            
            # Замер использования памяти после выполнения
            memory_after = psutil.virtual_memory().used
            
            # Вывод метрик
            execution_time = end_time - start_time
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            print(f"📊 Производительность:")
            print(f"   Время выполнения: {execution_time:.2f} сек")
            print(f"   Использовано памяти: {memory_used:.1f} MB")
            print(f"   Пиковая память: {psutil.virtual_memory().percent}%")
        
        return result
    
    @staticmethod
    def get_system_info() -> dict:
        """Получение информации о системе"""
        import platform
        
        info = {
            "system": platform.system(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "available_memory_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024
        }
        
        return info