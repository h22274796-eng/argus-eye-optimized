# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем системные зависимости для OpenCV и нейросети
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY backend/requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Открываем порт (Render сам его назначит, но для порядка укажем)
EXPOSE 8000

# Команда для запуска
CMD ["python", "backend/app.py"]