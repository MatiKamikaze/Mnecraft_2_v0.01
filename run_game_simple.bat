@echo off
title Minecraft_2_Ursina - Simple Launcher
color 0A

echo.
echo ======================================
echo  Minecraft_2_Ursina (Simple - bez venv)
echo ======================================
echo.

echo Sprawdzam Python...
python --version
if errorlevel 1 (
    color 0C
    echo [BLAD] Python nie zainstalowany!
    pause
    exit /b 1
)

echo.
echo Instaluję zaleznosci (bez venv)...
pip install -r requirements.txt --user
if errorlevel 1 (
    color 0C
    echo [BLAD] Instalacja nie powiodła sie.
    pause
    exit /b 1
)

echo.
echo Uruchamiam grę...
echo ======================================
echo.
python main.py
set RESULT=%ERRORLEVEL%
echo.
echo ======================================
echo Gra zakonczyla sie (kod: %RESULT%)
echo Nacisnij dowolny klawisz aby zamknac okno...
pause >nul

ENDLOCAL
exit /b %RESULT%
