# --- Preferencias de tema ---
import os
import json

def cargar_preferencias():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preferencias.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            return {"tema_oscuro": False, "idioma": "es"}
    return {"tema_oscuro": False, "idioma": "es"}

def cargar_preferencia_tema():
    return cargar_preferencias().get("tema_oscuro", False)

def cargar_preferencia_idioma():
    return cargar_preferencias().get("idioma", "es")


def guardar_preferencias(tema_oscuro, idioma):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preferencias.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"tema_oscuro": tema_oscuro, "idioma": idioma}, f, indent=2)
    except Exception:
        pass

def guardar_preferencia_tema(tema_oscuro):
    # Mantener compatibilidad, pero solo guarda el tema
    prefs = cargar_preferencias()
    guardar_preferencias(tema_oscuro, prefs.get("idioma", "es"))

def guardar_preferencia_idioma(idioma):
    prefs = cargar_preferencias()
    guardar_preferencias(prefs.get("tema_oscuro", False), idioma)
import tkinter as tk
from tkinter import ttk

IDIOMAS = {
    'es': {
        'buscar_archivo': "Buscar archivo",
        'copiar': "Copiar",
        'guardar': "Guardar",
        'anterior': "Anterior",
        'siguiente': "Siguiente",
        'archivo_seleccionado': "Archivo: ",
        'ningun_archivo': "ningún archivo.",
        'no_comentarios': "No se encontraron comentarios con el patrón # \"",
        'error_lectura': "No se pudo leer el archivo: ",
        'error_guardar': "No se pudo guardar la traducción: ",
        'error_no_archivo': "No hay archivo cargado para guardar.",
        'es': "Español",
        'en': "Inglés",
        'buscar_linea': "Buscar línea...",
        'ir_a_vacias': "Líneas vacías",
        'sin_lineas_vacias': "No se encontraron líneas vacías.",
        'error': "Error",
        'archivo_no_cargado': "No se ha cargado un archivo. Por favor, cargue un archivo primero.",
        'Tema': "Tema",
        'Auto_Rellenar': "Auto Rellenar",
        'Recargar': "Recargar",
        'configuraciones': "Configuraciones",
        'Escanear': "Escanear",
        'Ver_Lineas': "Ver Líneas",
        'Linea': "Línea",
        'Dialogo': "Diálogo",
        'Traduccion': "Traducción",
        'Borrar_Cache': "Borrar Cache",
        'Cerrar': "Cerrar"
    },
    'en': {
        'buscar_archivo': "Search file",
        'copiar': "Copy",
        'guardar': "Save",
        'anterior': "Previous",
        'siguiente': "Next",
        'archivo_seleccionado': "File selected: ",
        'ningun_archivo': "No file selected.",
        'no_comentarios': "No comments found with the pattern # \"",
        'error_lectura': "Could not read the file: ",
        'error_guardar': "Could not save the translation: ",
        'error_no_archivo': "No file loaded to save.",
        'es': "Spanish",
        'en': "English",
        'buscar_linea': "Search line...",
        'ir_a_vacias': "Empty Lines",
        'sin_lineas_vacias': "No empty lines found.",
        'error': "Error",
        'archivo_no_cargado': "No file loaded. Please load a file first.",
        'Tema': "Theme",
        'Auto_Rellenar': "Auto Fill",
        'Recargar': "Reload",
        'configuraciones': "Settings",
        'Escanear': "Scan",
        'Ver_Lineas': "View Lines",
        'Linea': "Line",
        'Dialogo': "Dialogue",
        'Traduccion': "Translation",
        'Borrar_Cache': "Clear Cache",
        'Cerrar': "Close"
    }
}

class Config:
    """
    Clase de configuración para gestionar estilos de temas en Tkinter usando ttk.Style
    """
    
    @staticmethod
    def aplicar_tema(root, oscuro=True):
        estilo = ttk.Style()
        tema = coloresOscuros if oscuro else coloresClaros
        
        estilo.configure("TFrame", background=tema['fondo'])
        estilo.configure("TLabel", background=tema['fondo'], foreground="white" if oscuro else "black")
        estilo.configure("TButton", background=tema['boton'], foreground="white", padding=6, font=('Arial', 12))
        estilo.map("TButton",
            background=[("active", tema['botonb'])],
            relief=[("pressed", "sunken")]
        )
        
        root.configure(bg=tema['fondo'])

# ----------------------------------------------------------------
####### Configuraciones ###########
coloresClaros = {
    'boton' : '#4CAF50',
    'botonb' : '#45a049',
    'fondo' : '#e6e6e6'
}

coloresOscuros = {
    'boton' : '#898ED6',
    'botonb' : '#6C70A8',
    'fondo' : '#1E1E1E'
}

idiomaX = 'es'
