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
        'Tema': 'Tema'

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
        'Tema': 'Theme'
    }
}




# configs.py

class Config:
    @staticmethod
    def tema_oscuro():
        return {
            "background_color": "#1E1E1E",
            "text_color": "white",
            "button_style": """
                QPushButton {
                    background-color: #2E2E2E;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #3E3E3E;
                }
                QPushButton:disabled {
                    background-color: #555;
                }
            """
        }

    @staticmethod
    def tema_claro():
        return {
            "background_color": fondoC['fondoC'],
            "text_color": "black",
            "button_style": """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                }
            """
        }


















# ----------------------------------------------------------------

####### Configuraciones / Configurations ###########


#### color botones / Color Buttons
boton = {
    'boton' : '#4CAF50',
    'botonb' : '#45a049'

}


#### fondo / Background
fondoC = {
    'fondoC' : '#ebebeb'

}


#### idioma / language
idiomaX = 'es'