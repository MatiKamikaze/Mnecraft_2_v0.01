@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

title Minecraft_2_Ursina - Launcher
color 0A

echo.
echo ======================================
echo  Minecraft_2_Ursina - Game Launcher
echo ======================================
echo.

REM --- Sprawdzenie Python ---
echo Sprawdzam czy Python jest zainstalowany...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [BLAD] Python nie znaleziony w PATH!
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Python znaleziony.
    python --version
    echo.
)

REM --- Sprawdzenie requirements.txt ---
if not exist "requirements.txt" (
    color 0C
    echo [BLAD] requirements.txt nie znaleziony!
    echo.
    pause
    exit /b 1
)
echo [OK] requirements.txt znaleziony.
echo.

REM --- Tworzenie/aktywacja venv ---
echo Krok 1: Sprawdzam wirtualne srodowisko (venv)... 
if exist "venv\Scripts\activate.bat" (
    echo [OK] venv juz istnieje. Aktywuję...
    call "venv\Scripts\activate.bat"
) else (
    echo [INFO] Tworzę nowy venv (moze zajac chwile)... 
    python -m venv venv
    call "venv\Scripts\activate.bat"
)
echo.

REM --- Instalacja zaleznosci ---
echo Krok 2: Instaluję zaleznosci...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo [OK] Zaleznosci zainstalowane.
echo.

REM --- NOWY: Generowanie tekstur ---
echo Krok 3: Generuję tekstury (jeśli brak)... 
if not exist "assets\textures\grass.png" (
    echo Generuję pliki PNG tekstur...
    python assets\generate_textures.py
    if errorlevel 1 (
        echo [WARN] Nie udalo sie wygenerowac tekstur. Gra uruchomi sie bez tekstur.
    )
) else (
    echo [OK] Tekstury juz istnieja.
)
echo.

REM --- Uruchomienie gry ---
echo Krok 4: Uruchamiam grę...
echo ======================================
echo.
python main.py
set GAME_EXIT=%ERRORLEVEL%
echo.
echo ======================================

echo [OK] Gra zakonczyla sie (kod: %GAME_EXIT%)
echo Nacisnij dowolny klawisz aby zamknac okno...
pause >nul

ENDLOCAL
exit /b %GAME_EXIT%
