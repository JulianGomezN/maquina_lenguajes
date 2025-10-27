@echo off
chcp 65001 > nul
setlocal

REM Lanzar el convertidor interactivo (file dialog)
cd /d "%~dp0"
echo Abriendo diálogo para seleccionar archivo .md...
python convertir_dialogo.py

if %errorlevel% neq 0 (
    echo El script devolvió un error.
    pause
    exit /b %errorlevel%
)

echo Finalizado.
pause