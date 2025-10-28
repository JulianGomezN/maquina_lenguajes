#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertidor interactivo: pide al usuario un archivo .md mediante un diálogo,
limpia caracteres Unicode problemáticos, genera un PDF con pandoc y borra el
.md temporal.
"""
import os
import sys
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Local import: limpiar_unicode.py está en la misma carpeta
from limpiar_unicode import limpiar_unicode


def seleccionar_md():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title='Seleccionar archivo Markdown (.md)',
        filetypes=[('Markdown', '*.md'), ('Text', '*.txt'), ('All files', '*.*')]
    )
    root.destroy()
    return file_path


def ejecutar_pandoc(md_path, pdf_path, header_path=None, resource_path=None):
    # Ejecutar pandoc con pdflatex y table of contents
    cmd = [
        'pandoc',
        '-f', 'markdown',
        '-t', 'pdf',
        '--pdf-engine=pdflatex',
        '--toc',
    ]
    if header_path:
        cmd.extend(['--include-in-header', header_path])
    if resource_path:
        # Indicar a pandoc la carpeta donde buscar recursos relativos (imágenes)
        cmd.extend(['--resource-path', resource_path])
    cmd.extend(['-o', pdf_path, md_path])

    print('Ejecutando:', ' '.join(cmd))
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result


def main():
    md_original = seleccionar_md()
    if not md_original:
        print('No se seleccionó ningún archivo. Saliendo.')
        return

    if not md_original.lower().endswith('.md'):
        # preguntar si convertir de todas formas
        tk.messagebox.showerror('Error', 'Por favor seleccione un archivo con extensión .md')
        return

    dirpath = os.path.dirname(md_original)
    base = os.path.splitext(os.path.basename(md_original))[0]

    md_limpio = os.path.join(dirpath, f"{base}_limpio.md")
    pdf_salida = os.path.join(dirpath, f"{base}.pdf")

    # 1) Limpiar unicode - llamar a la función si está disponible
    try:
        ok = limpiar_unicode(md_original, md_limpio)
        if not ok:
            tk.messagebox.showerror('Error', 'Fallo al limpiar el archivo Markdown.')
            return
    except Exception as e:
        # Fallback: intentar llamar al script como proceso
        print('Import falla, intentando ejecutar como script:', e)
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'limpiar_unicode.py'), md_original, md_limpio]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(p.stdout)
        if p.returncode != 0:
            tk.messagebox.showerror('Error', f'Fallo al limpiar el archivo.\n{p.stderr}')
            return

    # 2) Crear header temporal con margen EXACTO 2.54cm y convertir con pandoc
    import tempfile
    header_fd = None
    header_path = None
    try:
        # crear header temporal en la misma carpeta del markdown para evitar rutas relativas
        fd, header_path = tempfile.mkstemp(prefix='header_', suffix='.tex', dir=dirpath)
        header_fd = fd
        with os.fdopen(fd, 'w', encoding='utf-8') as hf:
            hf.write('\\usepackage[utf8]{inputenc}\n')
            hf.write('\\usepackage[spanish]{babel}\n')
            hf.write('\\usepackage{geometry}\n')
            hf.write('\\geometry{letterpaper,margin=2.54cm}\n')
            hf.write('\\usepackage{graphicx}\n')
            # Forzar que las figuras se coloquen donde aparecen en el Markdown
            hf.write('\\usepackage{float}\n')
            hf.write('\\floatplacement{figure}{H}\n')
            # Permitir barreras de floats si se desea usar \FloatBarrier
            hf.write('\\usepackage{placeins}\n')
            # Ajustar automáticamente las imágenes para que no excedan el ancho ni
            # el alto disponible en la página; se mantiene la relación de aspecto.
            # Usar directamente claves de graphicx: limitar al ancho de la línea y
            # al 90% de la altura de texto para evitar que una imagen ocupe toda la página.
            hf.write('\\setkeys{Gin}{width=\\linewidth,height=0.9\\textheight,keepaspectratio}\n')
        # Pasar la carpeta del markdown como resource-path para que pandoc
        # encuentre imágenes referenciadas con rutas relativas (por ejemplo images/...).
        res = ejecutar_pandoc(md_limpio, pdf_salida, header_path=header_path, resource_path=dirpath)
    finally:
        # borrar header temporal después de la conversión
        try:
            if header_path and os.path.exists(header_path):
                os.remove(header_path)
        except Exception as e:
            print('Advertencia: no se pudo borrar header temporal:', e)
    if res.returncode != 0:
        # Mostrar error detallado
        msg = f"Error en pandoc (código {res.returncode})\n\nSTDOUT:\n{res.stdout}\n\nSTDERR:\n{res.stderr}"
        print(msg)
        tk.messagebox.showerror('Error en conversión', msg)
        return

    # 3) Borrar el .md limpio (temporal)
    try:
        os.remove(md_limpio)
    except Exception as e:
        print('Advertencia: no se pudo borrar el archivo temporal:', md_limpio, e)

    # 4) Abrir el PDF generado
    try:
        if sys.platform.startswith('win'):
            os.startfile(pdf_salida)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', pdf_salida])
        else:
            subprocess.run(['xdg-open', pdf_salida])
    except Exception as e:
        print('No se pudo abrir el PDF automáticamente:', e)

    tk.messagebox.showinfo('Conversión completa', f'PDF generado:\n{pdf_salida}')


if __name__ == '__main__':
    main()
