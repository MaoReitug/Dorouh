# --- Preferencias de tema ---
import os
import json

IDIOMAS_DISPONIBLES = ("es", "en")


def normalizar_idioma(idioma):
    return idioma if idioma in IDIOMAS_DISPONIBLES else "es"

def cargar_preferencias():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preferencias.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            return {"tema_oscuro": False, "idioma": "es", "backup_habilitado": True}
    return {"tema_oscuro": False, "idioma": "es", "backup_habilitado": True}

def cargar_preferencia_tema():
    return cargar_preferencias().get("tema_oscuro", False)

def cargar_preferencia_idioma():
    idioma = cargar_preferencias().get("idioma", "es")
    return normalizar_idioma(idioma)


def cargar_preferencia_backup():
    return bool(cargar_preferencias().get("backup_habilitado", True))


def guardar_preferencias(tema_oscuro, idioma, backup_habilitado=None):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preferencias.json")
    if backup_habilitado is None:
        backup_habilitado = bool(cargar_preferencias().get("backup_habilitado", True))
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"tema_oscuro": tema_oscuro, "idioma": idioma, "backup_habilitado": bool(backup_habilitado)}, f, indent=2)
    except Exception:
        pass

def guardar_preferencia_tema(tema_oscuro):
    # Mantener compatibilidad, pero solo guarda el tema
    prefs = cargar_preferencias()
    guardar_preferencias(tema_oscuro, prefs.get("idioma", "es"), prefs.get("backup_habilitado", True))

def guardar_preferencia_idioma(idioma):
    prefs = cargar_preferencias()
    guardar_preferencias(prefs.get("tema_oscuro", False), normalizar_idioma(idioma), prefs.get("backup_habilitado", True))


def guardar_preferencia_backup(habilitado):
    prefs = cargar_preferencias()
    guardar_preferencias(prefs.get("tema_oscuro", False), normalizar_idioma(prefs.get("idioma", "es")), bool(habilitado))
import tkinter as tk
from tkinter import ttk

IDIOMAS = {
    'es': {
        'buscar_archivo': "Buscar archivo",
        'copiar': "Copiar",
        'guardar': "Guardar",
        'anterior': "Anterior",
        'siguiente': "Siguiente",
        'archivo_seleccionado': "Archivo seleccionado:",
        'ningun_archivo': "Ningún archivo seleccionado",
        'no_comentarios': "No se encontraron comentarios con el patrón # \"",
        'error_lectura': "No se pudo leer el archivo: ",
        'error_guardar': "No se pudo guardar la traducción: ",
        'error_no_archivo': "No hay archivo cargado para guardar.",
        'Idioma': "Idioma",
        'es': "Español",
        'en': "Inglés",
        'buscar_linea': "Buscar línea...",
        'placeholder_texto_original': "[Texto original]",
        'placeholder_traduccion': "[Traducción]",
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
        'Borrar_Backups': "Borrar Backups",
        'Backups': "Backups",
        'Cerrar': "Cerrar",
        'modo_visual': "Modo visual",
        'placeholder_desactivado': "está desactivado por ahora.",
        'placeholder_proximo': "Se implementará en siguientes pasos.",
        'copiado': "Copiado",
        'texto_copiado': "Texto copiado al portapapeles.",
        'gestion_repetidos': "Gestión de diálogos repetidos",
        'Lineas': "Líneas",
        'Traducciones': "Traducciones",
        'selecciona_dialogo_editar': "Selecciona un diálogo para editar sus traducciones:",
        'traduccion_personalizada': "O escribe una traducción personalizada:",
        'aplicar_traduccion_todas': "Aplicar traducción a todas las líneas",
        'traduccion_a': "Traducción A",
        'traduccion_b': "Traducción B",
        'advertencia': "Advertencia",
        'debes_seleccionar_dialogo': "Debes seleccionar un diálogo.",
        'aplicado': "Aplicado",
        'cambio_visual_aplicado': "Cambio visual aplicado (sin persistencia).",
        'auto_guardar_nav': "Auto-guardar al navegar",
        'guardar_en_duplicadas': "Guardar en duplicadas",
        'cargando_archivo': "Cargando archivo...",
        'total_lineas': "Total",
        'completas': "Completas",
        'vacias': "Vacías",
        'info': "Info",
        'sin_repetidos': "No se encontraron diálogos repetidos para aplicar automáticamente.",
        'sin_traducciones': "(sin traducciones)",
        'debes_elegir_traduccion': "Debes elegir o escribir una traducción.",
        'lineas_invalidas': "líneas inválidas",
        'aplicadas_en': "Traducción aplicada en",
        'lineas': "líneas",
        'sin_repetidos_restantes': "No quedan grupos repetidos pendientes.",
        'deshacer': "Deshacer",
        'sin_historial': "No hay cambios para deshacer.",
        'error_deshacer': "No se pudo deshacer: ",
        'deshecho': "Deshecho",
        'historial': "Historial",
        'historial_cambios': "Historial de cambios",
        'elige_deshacer': "Selecciona una acción y deshaz hasta ese punto:",
        'accion': "Acción",
        'cambios': "Cambios",
        'accion_manual': "Manual",
        'accion_auto': "Auto",
        'selecciona_historial': "Selecciona un elemento del historial.",
        'deshacer_seleccion': "Deshacer selección",
        'total': "Total"
        ,
        'archivos_eliminados': "archivos eliminados",
        'backup_automatico': "Backup automático",
        'backup_creado_en': "Backup creado en",
        'error_backup_guardado': "No se pudo crear backup, pero el archivo se guardó: ",
        'sin_archivo_para_backups': "No hay archivo cargado para gestionar backups.",
        'ventana_backups': "Backups del archivo",
        'sin_backups_disponibles': "No hay backups disponibles para este archivo.",
        'selecciona_backup': "Selecciona un backup.",
        'restaurar_backup': "Restaurar backup",
        'confirmar_restaurar_backup': "¿Restaurar este backup y reemplazar el archivo cargado actual?",
        'backup_restaurado': "Backup restaurado correctamente.",
        'error_restaurar_backup': "No se pudo restaurar el backup: ",
        'nombre': "Nombre",
        'fecha': "Fecha",
        'tamano': "Tamaño"
    },
    'en': {
        'buscar_archivo': "Search file",
        'copiar': "Copy",
        'guardar': "Save",
        'anterior': "Previous",
        'siguiente': "Next",
        'archivo_seleccionado': "Selected file:",
        'ningun_archivo': "No file selected.",
        'no_comentarios': "No comments found with the pattern # \"",
        'error_lectura': "Could not read the file: ",
        'error_guardar': "Could not save the translation: ",
        'error_no_archivo': "No file loaded to save.",
        'Idioma': "Language",
        'es': "Spanish",
        'en': "English",
        'buscar_linea': "Search line...",
        'placeholder_texto_original': "[Original text]",
        'placeholder_traduccion': "[Translation]",
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
        'Borrar_Backups': "Delete Backups",
        'Backups': "Backups",
        'Cerrar': "Close",
        'modo_visual': "Visual mode",
        'placeholder_desactivado': "is disabled for now.",
        'placeholder_proximo': "It will be implemented in the next steps.",
        'copiado': "Copied",
        'texto_copiado': "Text copied to clipboard.",
        'gestion_repetidos': "Repeated dialogues management",
        'Lineas': "Lines",
        'Traducciones': "Translations",
        'selecciona_dialogo_editar': "Select a dialogue to edit its translations:",
        'traduccion_personalizada': "Or type a custom translation:",
        'aplicar_traduccion_todas': "Apply translation to all lines",
        'traduccion_a': "Translation A",
        'traduccion_b': "Translation B",
        'advertencia': "Warning",
        'debes_seleccionar_dialogo': "You must select a dialogue.",
        'aplicado': "Applied",
        'cambio_visual_aplicado': "Visual change applied (not persisted).",
        'auto_guardar_nav': "Auto-save on navigation",
        'guardar_en_duplicadas': "Save in duplicates",
        'cargando_archivo': "Loading file...",
        'total_lineas': "Total",
        'completas': "Completed",
        'vacias': "Empty",
        'info': "Info",
        'sin_repetidos': "No repeated dialogues were found for automatic apply.",
        'sin_traducciones': "(no translations)",
        'debes_elegir_traduccion': "You must choose or type a translation.",
        'lineas_invalidas': "invalid lines",
        'aplicadas_en': "Translation applied to",
        'lineas': "lines",
        'sin_repetidos_restantes': "There are no repeated groups left to process.",
        'deshacer': "Undo",
        'sin_historial': "There are no changes to undo.",
        'error_deshacer': "Could not undo: ",
        'deshecho': "Undone",
        'historial': "History",
        'historial_cambios': "Change history",
        'elige_deshacer': "Select an action and undo up to that point:",
        'accion': "Action",
        'cambios': "Changes",
        'accion_manual': "Manual",
        'accion_auto': "Auto",
        'selecciona_historial': "Select a history item.",
        'deshacer_seleccion': "Undo selection",
        'total': "Total"
        ,
        'archivos_eliminados': "files deleted",
        'backup_automatico': "Automatic backup",
        'backup_creado_en': "Backup created at",
        'error_backup_guardado': "Backup could not be created, but file was saved: ",
        'sin_archivo_para_backups': "No file loaded to manage backups.",
        'ventana_backups': "File backups",
        'sin_backups_disponibles': "There are no backups available for this file.",
        'selecciona_backup': "Select a backup.",
        'restaurar_backup': "Restore backup",
        'confirmar_restaurar_backup': "Restore this backup and replace the currently loaded file?",
        'backup_restaurado': "Backup restored successfully.",
        'error_restaurar_backup': "Could not restore backup: ",
        'nombre': "Name",
        'fecha': "Date",
        'tamano': "Size"
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
        estilo.configure("TLabel", background=tema['fondo'], foreground="white" if oscuro else "#24323f")
        estilo.configure("TButton", background=tema['boton'], foreground="white", padding=6, font=('Arial', 12))
        estilo.map("TButton",
            background=[("active", tema['botonb'])],
            relief=[("pressed", "sunken")]
        )
        
        root.configure(bg=tema['fondo'])

# ----------------------------------------------------------------
####### Configuraciones ###########
coloresClaros = {
    'boton' : '#6EA886',
    'botonb' : '#5C9676',
    'fondo' : '#EEF2F6'
}

coloresOscuros = {
    'boton' : '#898ED6',
    'botonb' : '#6C70A8',
    'fondo' : '#1E1E1E'
}

idiomaX = 'es'
