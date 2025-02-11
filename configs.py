# configs.py
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
        'ir_a_vacias': 'líneas vacías',
        'sin_lineas_vacias': 'No se encontraron líneas vacías.',
        'error': 'Error',
        'archivo_no_cargado': 'No se ha cargado un archivo. Por favor, cargue un archivo primero.',
        'Tema': 'Tema',
        'Auto_Rellenar': "Auto Rellenar",
        'Recargar': "Recargar"

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
        'ir_a_vacias': 'Empty Lines',
        'sin_lineas_vacias': 'No empty lines found.',
        'error': 'Error',
        'archivo_no_cargado': 'No file loaded. Please load a file first.',
        'Tema': 'Theme',
        'Auto_Rellenar': "auto line",
        'Recargar': "Reload"
    }
}




# configs.py

class Config:
    
    @staticmethod
    def tema_oscuro(oscuro):
        return {
            "background_color": oscuro['fondo'],
            "text_color": "white",
            "button_style": f"""
                QPushButton {{
                    background-color: {oscuro['boton']};
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: {oscuro['botonb']};
                }}
                QPushButton:disabled {{
                    background-color: #555;
                }}
            """
        }

    @staticmethod
    def tema_claro(claro):
        return {
            "background_color": claro['fondo'],
            "text_color": "black",
            "button_style": f"""
                QPushButton {{
                    background-color: {claro['boton']};
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: {claro['botonb']};
                }}
                QPushButton:disabled {{
                    background-color: #ccc;
                }}
            """
        }

    @staticmethod
    def boton_estilo(boton):
        """ Define el estilo de los botones """
        # Usamos el diccionario 'boton' para acceder a los colores dinámicamente
        return f"""
            QPushButton {{
                background-color: {boton["boton"]};
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {boton["botonb"]};
            }}
            QPushButton:disabled {{
                background-color: #ccc;
            }}
        """














# ----------------------------------------------------------------

####### Configuraciones / Configurations ###########




coloresClaros = {

    #### color botones / Color Buttons
    'boton' : '#4CAF50',
    'botonb' : '#45a049',

    #### fondo / Background
    'fondo' : '#ebebeb'
}

coloresOscuros = {

    #### color botones / Color Buttons
    'boton' : '#898ED6',
    'botonb' : '#6C70A8',

    #### fondo / Background
    'fondo' : '#1E1E1E'
}



#### idioma / language
idiomaX = 'es'
