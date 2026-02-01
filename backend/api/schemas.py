"""
Pydantic схемы для валидации данных API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DetectionBBox(BaseModel):
    """Схема для bounding box"""
    x: float = Field(..., description="X координата левого верхнего угла")
    y: float = Field(..., description="Y координата левого верхнего угла")
    width: float = Field(..., description="Ширина bounding box")
    height: float = Field(..., description="Высота bounding box")

class GPSCoordinates(BaseModel):
    """Схема для GPS координат"""
    latitude: float = Field(..., description="Широта")
    longitude: float = Field(..., description="Долгота")
    altitude: Optional[float] = Field(None, description="Высота")
    accuracy_meters: Optional[float] = Field(None, description="Точность в метрах")
    calculation_method: Optional[str] = Field(None, description="Метод расчета координат")

class Detection(BaseModel):
    """Схема для детекции объекта"""
    class_name: str = Field(..., description="Название класса объекта")
    class_id: int = Field(..., description="ID класса")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность детекции")
    bbox: DetectionBBox = Field(..., description="Bounding box объекта")
    coordinates: Optional[GPSCoordinates] = Field(None, description="GPS координаты объекта")

class DetectionRequest(BaseModel):
    """Схема для запроса детекции"""
    confidence_threshold: float = Field(0.25, ge=0.0, le=1.0, description="Порог уверенности")
    use_sahi: bool = Field(True, description="Использовать ли SAHI для слайсинга")
    optimize_for_cpu: bool = Field(True, description="Использовать ли CPU оптимизации")

class DetectionResponse(BaseModel):
    """Схема для ответа детекции"""
    task_id: str = Field(..., description="ID задачи обработки")
    status: str = Field(..., description="Статус обработки")
    processing_time: float = Field(..., description="Время обработки в секундах")
    detections_count: int = Field(..., description="Количество обнаруженных объектов")
    detections: List[Detection] = Field([], description="Список детекций")
    has_gps: bool = Field(False, description="Есть ли GPS координаты")
    timestamp: datetime = Field(..., description="Временная метка обработки")

class ComparisonMethod(str, Enum):
    """Методы сравнения изображений"""
    SSIM = "ssim"
    ABSDIFF = "absdiff"
    OPTICAL_FLOW = "opticalflow"

class ComparisonRequest(BaseModel):
    """Схема для запроса сравнения изображений"""
    method: ComparisonMethod = Field(ComparisonMethod.SSIM, description="Метод сравнения")
    threshold: int = Field(30, ge=1, le=100, description="Порог чувствительности")

class ChangeDetection(BaseModel):
    """Схема для детекции изменений"""
    bbox: List[int] = Field(..., description="Bounding box изменения [x, y, width, height]")
    area: float = Field(..., description="Площадь изменения в пикселях")
    center: List[int] = Field(..., description="Центр изменения [x, y]")

class ComparisonResponse(BaseModel):
    """Схема для ответа сравнения изображений"""
    method: str = Field(..., description="Использованный метод")
    similarity_score: Optional[float] = Field(None, description="Оценка схожести (только для SSIM)")
    change_count: int = Field(..., description="Количество изменений")
    changes: List[ChangeDetection] = Field([], description="Список изменений")
    image1_size: List[int] = Field(..., description="Размер первого изображения")
    image2_size: List[int] = Field(..., description="Размер второго изображения")
    timestamp: datetime = Field(..., description="Временная метка")

class ExportFormat(str, Enum):
    """Форматы экспорта"""
    KML = "kml"
    JSON = "json"
    CSV = "csv"
    GEOJSON = "geojson"

class ExportRequest(BaseModel):
    """Схема для запроса экспорта"""
    detections: List[Detection] = Field(..., description="Список детекций для экспорта")
    format: ExportFormat = Field(ExportFormat.KML, description="Формат экспорта")
    include_metadata: bool = Field(True, description="Включать ли метаданные")

class HealthResponse(BaseModel):
    """Схема для ответа проверки здоровья"""
    status: str = Field(..., description="Статус системы")
    model_ready: bool = Field(..., description="Готова ли модель")
    timestamp: datetime = Field(..., description="Временная метка")
    system: Dict[str, Any] = Field(..., description="Информация о системе")

class StatisticsResponse(BaseModel):
    """Схема для ответа статистики"""
    total_tasks: int = Field(..., description="Всего задач обработки")
    total_detections: int = Field(..., description="Всего обнаруженных объектов")
    avg_processing_time: float = Field(..., description="Среднее время обработки")
    tasks_with_gps: int = Field(..., description="Количество задач с GPS")
    gps_percentage: float = Field(..., description="Процент задач с GPS")
    class_statistics: List[Dict[str, Any]] = Field(..., description="Статистика по классам")
    daily_statistics: List[Dict[str, Any]] = Field(..., description="Ежедневная статистика")

class TaskStatus(str, Enum):
    """Статусы задач"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class TaskInfo(BaseModel):
    """Схема для информации о задаче"""
    task_id: str = Field(..., description="ID задачи")
    status: TaskStatus = Field(..., description="Статус задачи")
    created_at: datetime = Field(..., description="Время создания")
    processing_time: Optional[float] = Field(None, description="Время обработки")
    detections_count: Optional[int] = Field(None, description="Количество детекций")
    has_gps: Optional[bool] = Field(None, description="Есть ли GPS данные")

class ModelInfo(BaseModel):
    """Схема для информации о модели"""
    name: str = Field(..., description="Имя модели")
    description: str = Field(..., description="Описание модели")
    classes: List[str] = Field(..., description="Список классов")
    optimized: bool = Field(..., description="Оптимизирована ли для CPU")
    supports_sahi: bool = Field(..., description="Поддерживает ли SAHI")

class OptimizationConfig(BaseModel):
    """Схема для конфигурации оптимизаций"""
    use_openvino: bool = Field(..., description="Использовать OpenVINO")
    use_onnx: bool = Field(..., description="Использовать ONNX Runtime")
    use_sahi: bool = Field(..., description="Использовать SAHI")
    max_image_size: int = Field(..., description="Максимальный размер изображения")
    cpu_threads: int = Field(..., description="Количество потоков CPU")
    batch_size: int = Field(..., description="Размер пакета")

# Валидаторы
@validator('confidence')
def validate_confidence(cls, v):
    """Валидация уверенности детекции"""
    if not 0 <= v <= 1:
        raise ValueError('Confidence must be between 0 and 1')
    return v

@validator('bbox')
def validate_bbox(cls, v):
    """Валидация bounding box"""
    if v.width <= 0 or v.height <= 0:
        raise ValueError('Bounding box dimensions must be positive')
    return v

@validator('coordinates')
def validate_coordinates(cls, v):
    """Валидация координат GPS"""
    if v:
        if not -90 <= v.latitude <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        if not -180 <= v.longitude <= 180:
            raise ValueError('Longitude must be between -180 and 180')
    return v