#!/bin/bash

echo "======================================================"
echo "🚀 Запуск Argus Eye в режиме разработки"
echo "======================================================"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено"
    echo "Запустите сначала setup.sh"
    exit 1
fi

# Активация виртуального окружения
source venv/bin/activate

echo "✅ Виртуальное окружение активировано"

# Проверка необходимых файлов
echo ""
echo "🔍 Проверка необходимых файлов..."

if [ ! -f "backend/app.py" ]; then
    echo "❌ Файл backend/app.py не найден"
    exit 1
fi

if [ ! -f "frontend/streamlit_app.py" ]; then
    echo "❌ Файл frontend/streamlit_app.py не найден"
    exit 1
fi

echo "✅ Все необходимые файлы найдены"

# Проверка модели YOLO
echo ""
echo "🤖 Проверка модели YOLO..."

if [ ! -f "backend/models/yolov8n.pt" ]; then
    echo "⚠️ Модель YOLO не найдена. Попытка скачать..."
    python -c "
from ultralytics import YOLO
try:
    model = YOLO('yolov8n.pt')
    model.save('backend/models/yolov8n.pt')
    print('✅ Модель загружена')
except Exception as e:
    print(f'❌ Ошибка загрузки модели: {e}')
    exit(1)
"
fi

echo "✅ Модель YOLO проверена"

# Очистка старых логов
echo ""
echo "🧹 Очистка старых логов..."
rm -f logs/*.log 2>/dev/null
echo "✅ Логи очищены"

# Запуск бэкенда в фоновом режиме
echo ""
echo "🔧 Запуск бэкенда API..."
cd backend
python app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Проверка запуска бэкенда
sleep 3
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Бэкенд запущен (PID: $BACKEND_PID)"
else
    echo "❌ Не удалось запустить бэкенд"
    echo "Смотрите логи: logs/backend.log"
    exit 1
fi

echo "Жду 5 секунд для полного запуска бэкенда..."
sleep 5

# Проверка доступности API
echo ""
echo "🔌 Проверка доступности API..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API доступен на http://localhost:8000"
else
    echo "❌ API недоступен"
    echo "Смотрите логи: logs/backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Запуск фронтенда
echo ""
echo "🎨 Запуск веб-интерфейса..."
cd ../frontend
streamlit run streamlit_app.py > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 2
if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Фронтенд запущен (PID: $FRONTEND_PID)"
else
    echo "❌ Не удалось запустить фронтенд"
    echo "Смотрите логи: logs/frontend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "======================================================"
echo "✅ ARGUS EYE ЗАПУЩЕН!"
echo "======================================================"
echo ""
echo "🌐 ОТКРОЙТЕ В БРАУЗЕРЕ:"
echo "   • Веб-интерфейс: http://localhost:8501"
echo "   • API документация: http://localhost:8000/docs"
echo "   • API Health Check: http://localhost:8000/health"
echo ""
echo "📊 МОНИТОРИНГ:"
echo "   • Логи бэкенда: tail -f logs/backend.log"
echo "   • Логи фронтенда: tail -f logs/frontend.log"
echo ""
echo "🛑 ДЛЯ ОСТАНОВКИ:"
echo "   1. Нажмите Ctrl+C в этом окне"
echo "   2. Или используйте: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "======================================================"

# Ожидание завершения (при нажатии Ctrl+C)
trap "echo ''; echo '🛑 Остановка системы...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Бесконечное ожидание
while true; do
    sleep 60
done