@echo off
title Argus Eye System Control
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

echo ==========================================
echo       STARTING ARGUS EYE SYSTEM
echo ==========================================

:: Шаг 0: Очистка портов от старых запусков
echo [0/2] Cleaning up old processes...
taskkill /F /IM python.exe /T >nul 2>&1

:: Шаг 1: Запуск Бэкенда в отдельном окне
echo [1/2] Starting API Backend...
start "Argus Eye API" cmd /k "venv\Scripts\activate && uvicorn backend.app:app --host 127.0.0.1 --port 8000"

:: Шаг 2: Ожидание инициализации нейросети
echo Waiting for backend to initialize (10 sec)...
timeout /t 10 /nobreak > nul

:: Шаг 3: Запуск Фронтенда
echo [2/2] Starting Streamlit Frontend...
venv\Scripts\activate && streamlit run frontend/streamlit_app.py

pause