@echo off
chcp 65001 >nul
echo ===================================================
echo   Quartier Prague — Yerel Isletme Web Studyosu
echo ===================================================
echo.
echo [1/2] Python kutuphaneleri kontrol ediliyor...
python -m pip install -r requirements.txt --quiet
echo [2/2] Sunucu baslatiliyor: http://127.0.0.1:8765
start http://127.0.0.1:8765
python server.py
pause
