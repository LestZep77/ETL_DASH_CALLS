@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo  Preparando entorno - ETL DASH CALLS
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_DIR=%%~fI"
set "VENV_DIR=%PROJECT_DIR%\.venv"
set "REQUIREMENTS=%PROJECT_DIR%\requirements.txt"
set "EXAMPLE_ENV=%PROJECT_DIR%\.env.example"
set "ROOT_ENV=%PROJECT_DIR%\.env"

set "PYTHON_CMD="

py -3.11 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
) else (
    py -3.14 -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3.14"
    ) else (
        python -c "import sys" >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_CMD=python"
        )
    )
)

if not defined PYTHON_CMD (
    echo [ERROR] No se encontro un interprete de Python compatible.
    echo Instala Python 3.11 o 3.14 y vuelve a ejecutar este script.
    pause
    exit /b 1
)

echo [OK] Python detectado: %PYTHON_CMD%

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] No fue posible crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo [OK] Entorno virtual existente: %VENV_DIR%
)

echo [INFO] Actualizando pip...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Fallo la actualizacion de pip.
    pause
    exit /b 1
)

echo [INFO] Instalando dependencias...
"%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%\.env" (
    if not exist "%PROJECT_DIR%\config\.env" (
        echo.
        echo [INFO] No se encontro un archivo .env activo.
        if exist "%EXAMPLE_ENV%" (
            copy /Y "%EXAMPLE_ENV%" "%ROOT_ENV%" >nul
            if errorlevel 1 (
                echo [ERROR] No fue posible crear el archivo .env desde .env.example.
                pause
                exit /b 1
            )
            echo [OK] Se creo .env desde .env.example. Completa tus credenciales.
        ) else (
            echo Copia .env.example a .env o config\.env y completa tus credenciales.
        )
    )
)

echo.
echo [OK] Entorno listo.
echo Siguiente paso: completar credenciales y ejecutar:
echo   "%VENV_DIR%\Scripts\python.exe" "%PROJECT_DIR%\main.py"
echo.
pause