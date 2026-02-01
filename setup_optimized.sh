#!/bin/bash

echo "🚀 Настройка оптимизированного Argus Eye для CPU"

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активация
source venv/bin/activate

# Установка зависимостей бэкенда
echo "📦 Установка зависимостей бэкенда..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Установка зависимостей фронтенда
echo "🎨 Установка зависимостей фронтенда..."
pip install -r frontend/requirements.txt

# Установка дополнительных оптимизаций
echo "⚡ Установка оптимизаций для CPU..."
pip install openvino openvino-dev  # Intel оптимизация
pip install onnx onnxruntime       # ONNX runtime
pip install sahi                    # Слайсинг для мелких объектов
pip install streamlit-folium        # Карты в Streamlit
pip install folium                  # Работа с картами
pip install exifread                # Чтение EXIF данных

# Создание структуры директорий
echo "📁 Создание структуры директорий..."
mkdir -p backend/models
mkdir -p backend/utils
mkdir -p backend/api
mkdir -p backend/services
mkdir -p frontend/pages
mkdir -p frontend/components
mkdir -p uploads
mkdir -p results
mkdir -p logs
mkdir -p exports

# Скачивание и оптимизация модели YOLO
echo "🤖 Подготовка оптимизированной модели YOLO..."
python -c "
import os
from pathlib import Path
from ultralytics import YOLO

# Пути к моделям
models_dir = Path('backend/models')
models_dir.mkdir(exist_ok=True)

# Скачиваем легкую модель
model_path = models_dir / 'yolov8n.pt'
if not model_path.exists():
    print('Скачивание YOLOv8n...')
    model = YOLO('yolov8n.pt')
    model.save(model_path)
    print(f'✅ Модель сохранена: {model_path}')
    
    # Пробуем оптимизировать для OpenVINO
    try:
        print('⚡ Оптимизация для OpenVINO...')
        model.export(format='openvino', imgsz=640)
        print('✅ Модель оптимизирована для OpenVINO')
    except Exception as e:
        print(f'⚠️ OpenVINO оптимизация не удалась: {e}')
        
    # Пробуем экспортировать в ONNX
    try:
        print('⚡ Экспорт в ONNX...')
        model.export(format='onnx', imgsz=640, simplify=True)
        print('✅ Модель экспортирована в ONNX')
    except Exception as e:
        print(f'⚠️ ONNX экспорт не удался: {e}')
else:
    print(f'✅ Модель уже существует: {model_path}')
"

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."
python -c "
from backend.utils.database import init_db
init_db()
print('✅ База данных создана')
"

# Проверка оптимизаций
echo "🔍 Проверка доступных оптимизаций..."
python -c "
try:
    import openvino.runtime as ov
    print('✅ OpenVINO доступен')
except:
    print('❌ OpenVINO не установлен')

try:
    import onnxruntime as ort
    print('✅ ONNX Runtime доступен')
except:
    print('❌ ONNX Runtime не установлен')

try:
    import sahi
    print('✅ SAHI доступен')
except:
    print('❌ SAHI не установлен')
"

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "📝 Инструкции по запуску:"
echo "1. Запустите бэкенд: cd backend && python app.py"
echo "2. Запустите фронтенд: cd frontend && streamlit run streamlit_app.py"
echo "3. Откройте http://localhost:8501 в браузере"
echo ""
echo "⚡ Оптимизации включены:"
echo "   - OpenVINO для Intel CPU"
echo "   - ONNX Runtime для ускорения"
echo "   - SAHI для мелких объектов"
echo "   - CPU оптимизации"