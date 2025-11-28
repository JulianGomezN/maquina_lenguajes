@echo off
chcp 65001 > nul

REM Cambiar al directorio del script y guardar el anterior
pushd "%~dp0"

echo Abriendo di�logo para seleccionar archivo .md...
echo Ejecutando script Python: convertir_dialogo.py
python convertir_dialogo.py

if %ERRORLEVEL% NEQ 0 (
    echo El script devolvi� un error.
    pause
    popd
    exit /b %ERRORLEVEL%
)

echo Finalizado.
pause
popd