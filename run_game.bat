@echo off
SETLOCAL

echo ------------------------------
echo Minecraft_2_Ursina - Uruchomienie gry
echo ------------------------------

REM --- Aktywuj virtualenv jeśli istnieje, inaczej utwórz i aktywuj ---
if exist "venv\Scripts\activate.bat" (
    echo Aktywacja istniejącego venv...
    call "venv\Scripts\activate.bat"
) else (
    echo Brak venv w ./venv. Tworzenie virtualenv (moze zajac chwile)...
    python -m venv venv
    if exist "venv\Scripts\activate.bat" (
        call "venv\Scripts\activate.bat"
    ) else (
        echo Nie udalo sie utworzyc venv. Upewnij sie, ze Python jest zainstalowany i w PATH.
    )
)

REM --- Zainstaluj zależności jeśli istnieje requirements.txt ---
if exist "requirements.txt" (
    echo Instalowanie zaleznosci z requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo Brak requirements.txt — pomijam instalacje zaleznosci.
)

REM --- Uruchom glowny skrypt gry ---
echo Uruchamiam python main.py ...
python main.py

REM --- Pozostaw okno otwarte by zobaczyc wyjscie/bledy ---
echo.
echo Gra zakonczona. Nacisnij dowolny klawisz aby zamknac okno.
pause >nul

ENDLOCAL
