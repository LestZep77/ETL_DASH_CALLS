@echo off
chcp 65001 >nul
echo ============================================
echo  Instalando Tarea Programada - ETL DASH CALLS
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_DIR=%%~fI"

REM Auto-detectar ruta del python del entorno virtual
set "PYTHON_PATH=%PROJECT_DIR%\.venv\Scripts\python.exe"
if not exist "%PYTHON_PATH%" (
    set "PYTHON_PATH=%PROJECT_DIR%\.venv\bin\python.exe"
)
if not exist "%PYTHON_PATH%" (
    echo [ERROR] No se encuentra el entorno virtual.
    echo Se busco en:
    echo   %PROJECT_DIR%\.venv\Scripts\python.exe
    echo   %PROJECT_DIR%\.venv\bin\python.exe
    echo Ejecuta primero: python -m venv .venv
    pause
    exit /b 1
)
echo [OK] Python encontrado: %PYTHON_PATH%

set "SCRIPT_PATH=%PROJECT_DIR%\main.py"

schtasks /create ^
    /tn "ETL_DASH_CALLS" ^
    /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" ^
    /sc weekly ^
    /d MON,TUE,WED,THU,FRI ^
    /st 08:00 ^
    /ri 180 ^
    /du 09:00 ^
    /f

if %errorlevel% equ 0 (
    echo.
    echo [OK] Tarea creada exitosamente
    echo.
    echo Programacion:
    echo   - Dias:    Lunes a Viernes
    echo   - Horario: 08:00 - 17:00
    echo   - Frecuencia: Cada 3 horas ^(08:00, 11:00, 14:00, 17:00^)
    echo.
    echo Para verificar: schtasks /query /tn ETL_DASH_CALLS
) else (
    echo [ERROR] Fallo al crear la tarea
)

pause
