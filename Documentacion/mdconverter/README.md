Convertidor Markdown -> PDF (mdconverter)

Descripción
-----------
Este pequeño convertidor permite seleccionar un archivo Markdown (.md) mediante un diálogo (file dialog), limpiar caracteres Unicode problemáticos, generar un PDF usando Pandoc (con índice automático) y eliminar el .md temporal que se genera durante el proceso.

Requerimientos
-------------
- Python 3.x
- Pandoc instalado y accesible en PATH
- Una distribución LaTeX instalada (por ejemplo MiKTeX) si desea salida PDF vía pdflatex

Uso (recomendado)
-----------------
1. Antes de convertir: abre tu archivo Markdown y elimina todo el contenido de la portada/manual que haya hasta la primera aparición de `\newpage` justo antes de la primera sección (por ejemplo, antes de `# 1. Marco Teórico`).
   - Razón: el convertidor genera su propia tabla de contenidos; si mantienes un índice manual, éste será incluido duplicado. Además la portada y el resto deben quedar en el documento de forma que Pandoc genere la TOC correctamente.

2. Ejecuta `convertir.bat` (en Windows) dentro de la carpeta `mdconverter`.
   - Se abrirá un diálogo para que selecciones el archivo `.md` que quieras convertir.

3. El script hará lo siguiente automáticamente:
   - Creará una versión limpia del Markdown (sufijo `_limpio.md`) en la misma carpeta del archivo seleccionado.
   - Ejecutará Pandoc para generar `nombre_original.pdf` en la misma carpeta.
   - Eliminará el archivo `_limpio.md` temporal al terminar.
   - Intentará abrir el PDF generado automáticamente.

Notas y recomendaciones
-----------------------
- Asegúrate de cerrar cualquier visor de PDF que esté abriendo el archivo de salida antes de volver a ejecutar el convertidor (evita problemas de permiso al sobrescribir).
- Si Pandoc falla por problemas de LaTeX o paquetes faltantes, revisa la salida de error que se mostrará en pantalla.
- Si deseas personalizar márgenes o headers, puedes editar el script `convertir_dialogo.py` para pasar `--include-in-header=...` a Pandoc.

Soporte
-------
Si necesitas que el convertidor use un header LaTeX concreto (portada, logo, etc.) o que mantenga la portada dentro del MD en lugar de quitarla, dime qué comportamiento deseas y lo adapto.
