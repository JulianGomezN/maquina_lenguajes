
@echo off
chcp 65001 > nul
setlocal

REM === CONFIGURA EL NOMBRE DE TU ARCHIVO MARKDOWN AQUÍ ===
set "MD=Tarea14_Limpio.md"

REM === CREA HEADER TEMPORAL CON MARGEN 2.54cm ===
set "HEADER=header.tex"
echo ^\usepackage[utf8]{inputenc}> %HEADER%
echo ^\usepackage[spanish]{babel}>> %HEADER%
echo ^\usepackage{geometry}>> %HEADER%
echo ^\geometry{a4paper,margin=2.54cm}>> %HEADER%

set "PDF=%MD:.md=.pdf%"

cd /d "d:\UN\2025-2\Lenguajes\Maquina\maquina_lenguajes\Documentacion"

echo Verificando archivo limpio existente...

rem Solo crear versión limpia si no existe o si el original es más nuevo
if not exist "Tarea14_Limpio.md" (
    echo Creando versión completamente limpia sin caracteres Unicode...
    python limpiar_unicode.py
    if %errorlevel% neq 0 (
        echo ✗ Error al limpiar caracteres Unicode
        pause
        exit /b 1
    )
) else (
    echo ✓ Archivo limpio ya existe: Tarea14_Limpio.md
)

if not exist "%MD%" (
    echo No se encuentra el archivo %MD%
    pause
    exit /b 1
)

REM === SI USAS HEADER ===
echo Convirtiendo %MD% a %PDF% usando header %HEADER%...
pandoc -f markdown -t pdf --pdf-engine=pdflatex --include-in-header="%HEADER%" --toc -o "%PDF%" "%MD%"


if %errorlevel% neq 0 (
    echo Error en la conversión.
    pause
    exit /b 1
) else (
    echo Conversion exitosa: %PDF%
    start "" "%PDF%"
)

REM Limpia el header temporal
del "%HEADER%" > nul 2>&1

pause