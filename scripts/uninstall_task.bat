@echo off
chcp 65001 >nul
echo =============================================
echo  Eliminando Tarea Programada - ETL DASH CALLS
echo =============================================
echo.

schtasks /delete /tn "ETL_DASH_CALLS" /f

if %errorlevel% equ 0 (
    echo [OK] Tarea eliminada exitosamente
) else (
    echo [INFO] La tarea no existe o ya fue eliminada
)

pause
