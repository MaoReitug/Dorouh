import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class Dorouh(QWidget):
    def __init__(self):
        super().__init__()

        # Definir el directorio actual del archivo
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        # Establecer el ícono de la ventana y la barra de tareas
        self.setWindowIcon(QIcon(os.path.join(directorio_actual, 'icon.png')))

        # Definir el título y tamaño de la ventana
        self.setWindowTitle("Dorouh v0.1")
        self.setGeometry(100, 100, 800, 600)

        # Inicialización de variables
        self.archivo_seleccionado = "Ningún archivo seleccionado"
        self.lineas = []
        self.indice_linea = 0
        self.indices_comentarios = []
        self.ruta_archivo = None
        self.idioma = 'es'  # Idioma predeterminado (español)

        # Diccionario de traducciones para español e inglés
        self.traducciones = {
            'es': {
                'buscar_archivo': "Buscar archivo",
                'copiar': "Copiar",
                'guardar': "Guardar",
                'anterior': "Anterior",
                'siguiente': "Siguiente",
                'archivo_seleccionado': "Archivo seleccionado: ",
                'ningun_archivo': "No se seleccionó ningún archivo.",
                'no_comentarios': "No se encontraron comentarios con el patrón # \"",
                'error_lectura': "No se pudo leer el archivo: ",
                'error_guardar': "No se pudo guardar la traducción: ",
                'error_no_archivo': "No hay archivo cargado para guardar.",
                'es': "Español",
                'en': "Inglés"
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
                'en': "English"
            }
        }

        self.initUI()

    def initUI(self):
        """ Configura la interfaz de usuario con los botones, etiquetas y áreas de texto """
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Barra superior
        top_layout = QHBoxLayout()

        # Etiqueta para mostrar el archivo seleccionado
        self.etiqueta_archivo = QLabel(self.traducciones[self.idioma]['ningun_archivo'])
        self.etiqueta_archivo.setFont(QFont('Arial', 12, QFont.Bold))
        self.etiqueta_archivo.setAlignment(Qt.AlignLeft)
        top_layout.addWidget(self.etiqueta_archivo)

        # Botón para buscar un archivo
        self.boton_buscar = QPushButton(self.traducciones[self.idioma]['buscar_archivo'], self)
        self.boton_buscar.setStyleSheet(self.boton_estilo())
        self.boton_buscar.clicked.connect(self.seleccionar_archivo)
        top_layout.addWidget(self.boton_buscar)

        # Botón para cambiar idioma
        self.boton_idioma = QPushButton(self.traducciones[self.idioma][self.idioma], self)
        self.boton_idioma.setStyleSheet(self.boton_estilo())
        self.boton_idioma.setFixedWidth(100)  # Hacer el botón más pequeño
        self.boton_idioma.clicked.connect(self.cambiar_idioma)
        top_layout.addWidget(self.boton_idioma, alignment=Qt.AlignCenter)

        layout.addLayout(top_layout)

        # Área para mostrar el texto seleccionado para traducir
        self.texto_seleccionable = QTextEdit(self)
        self.texto_seleccionable.setFont(QFont('Arial', 12))
        self.texto_seleccionable.setReadOnly(True)
        self.texto_seleccionable.setStyleSheet("QTextEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; height: 80px; }")
        layout.addWidget(self.texto_seleccionable)

        # Botón para copiar el texto seleccionado
        self.boton_copiar = QPushButton(self.traducciones[self.idioma]['copiar'], self)
        self.boton_copiar.setStyleSheet(self.boton_estilo())
        self.boton_copiar.clicked.connect(self.copiar_texto)
        layout.addWidget(self.boton_copiar)

        # Área para mostrar la traducción
        self.cuadro_traduccion = QTextEdit(self)
        self.cuadro_traduccion.setFont(QFont('Arial', 12))
        self.cuadro_traduccion.setStyleSheet("QTextEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; height: 80px; }")
        layout.addWidget(self.cuadro_traduccion)

        # Botones para navegar entre líneas y guardar traducción
        boton_layout = QHBoxLayout()

        # Botón para ir a la línea anterior
        self.boton_anterior = QPushButton(self.traducciones[self.idioma]['anterior'], self)
        self.boton_anterior.setEnabled(False)
        self.boton_anterior.setStyleSheet(self.boton_estilo())
        self.boton_anterior.clicked.connect(self.linea_anterior)
        boton_layout.addWidget(self.boton_anterior)

        # Botón para guardar la traducción
        self.boton_guardar = QPushButton(self.traducciones[self.idioma]['guardar'], self)
        self.boton_guardar.setEnabled(False)
        self.boton_guardar.setStyleSheet(self.boton_estilo())
        self.boton_guardar.clicked.connect(self.guardar_traduccion)
        boton_layout.addWidget(self.boton_guardar)

        # Botón para ir a la línea siguiente
        self.boton_siguiente = QPushButton(self.traducciones[self.idioma]['siguiente'], self)
        self.boton_siguiente.setEnabled(False)
        self.boton_siguiente.setStyleSheet(self.boton_estilo())
        self.boton_siguiente.clicked.connect(self.linea_siguiente)
        boton_layout.addWidget(self.boton_siguiente)

        layout.addLayout(boton_layout)
        self.setLayout(layout)

    def boton_estilo(self):
        """ Define el estilo de los botones """
        return """
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

    def cambiar_idioma(self):
        """ Cambia el idioma de la interfaz entre español e inglés """
        self.idioma = 'en' if self.idioma == 'es' else 'es'

        # Actualiza los textos de los botones
        self.boton_buscar.setText(self.traducciones[self.idioma]['buscar_archivo'])
        self.boton_copiar.setText(self.traducciones[self.idioma]['copiar'])
        self.boton_guardar.setText(self.traducciones[self.idioma]['guardar'])
        self.boton_anterior.setText(self.traducciones[self.idioma]['anterior'])
        self.boton_siguiente.setText(self.traducciones[self.idioma]['siguiente'])
        self.boton_idioma.setText(self.traducciones[self.idioma][self.idioma])

        # Actualiza la etiqueta del archivo seleccionado
        self.etiqueta_archivo.setText(f"{self.traducciones[self.idioma]['archivo_seleccionado']} {os.path.basename(self.ruta_archivo) if self.ruta_archivo else self.traducciones[self.idioma]['ningun_archivo']}")

    def seleccionar_archivo(self):
        """ Abre un cuadro de diálogo para seleccionar un archivo """
        archivo, _ = QFileDialog.getOpenFileName(self, self.traducciones[self.idioma]['buscar_archivo'], "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.ruta_archivo = archivo
            self.etiqueta_archivo.setText(f"{self.traducciones[self.idioma]['archivo_seleccionado']} {os.path.basename(archivo)}")
            self.cargar_archivo(archivo)
        else:
            self.etiqueta_archivo.setText(self.traducciones[self.idioma]['ningun_archivo'])

    def cargar_archivo(self, archivo):
        """ Carga el contenido del archivo y extrae los comentarios con el patrón '#' """
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                self.lineas = f.readlines()

            # Identifica las líneas que contienen comentarios válidos
            self.indices_comentarios = [i for i, linea in enumerate(self.lineas) if '#' in linea and '"' in linea.split('#', 1)[1]]
            self.indice_linea = 0

            if self.indices_comentarios:
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                QMessageBox.information(self, self.traducciones[self.idioma]['no_comentarios'], self.traducciones[self.idioma]['no_comentarios'])
        except Exception as e:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_lectura'], f"{self.traducciones[self.idioma]['error_lectura']} {e}")

    def cargar_linea(self, indice):
        """ Carga una línea específica con el comentario y su traducción """
        if 0 <= indice < len(self.indices_comentarios):
            indice_comentario = self.indices_comentarios[indice]
            linea_comentario = self.lineas[indice_comentario].strip()

            # Extrae el texto después del comentario '#'
            if '#' in linea_comentario:
                comentario = linea_comentario.split('#', 1)[1].strip()
                if '"' in comentario:
                    texto = comentario.split('"')[1]
                    
                    # Detecta si hay una letra antes de las comillas
                    letra = comentario[0] if comentario[0].isalpha() else ""
                    texto_con_numero_linea = f"{indice_comentario + 1} {letra}: {texto}"
                else:
                    texto_con_numero_linea = f"{indice_comentario + 1}: {comentario} "
            else:
                texto_con_numero_linea = f"{indice_comentario + 1}:"

            # Actualiza el área de texto seleccionable y la traducción
            traduccion = ""
            if indice_comentario + 1 < len(self.lineas):
                linea_traduccion = self.lineas[indice_comentario + 1].strip()
                if '"' in linea_traduccion:
                    traduccion = linea_traduccion.split('"')[1]

            self.actualizar_texto_traducir(texto_con_numero_linea, traduccion)

    def actualizar_texto_traducir(self, texto, traduccion):
        """ Actualiza los cuadros de texto con la línea seleccionada y la traducción """
        self.texto_seleccionable.setPlainText(texto)
        self.cuadro_traduccion.setPlainText(traduccion)

    def copiar_texto(self):
        """ Copia el texto seleccionado al portapapeles """
        texto = self.texto_seleccionable.toPlainText().strip()
        texto_sin_numero = texto.split(':', 1)[1].strip() if ':' in texto else texto
        QApplication.clipboard().setText(texto_sin_numero)

    def guardar_traduccion(self):
        """ Guarda la traducción en el archivo seleccionado """
        if not self.ruta_archivo:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_no_archivo'], self.traducciones[self.idioma]['error_no_archivo'])
            return

        try:
            indice_comentario = self.indices_comentarios[self.indice_linea]
            traduccion = self.cuadro_traduccion.toPlainText().strip()

            if indice_comentario + 1 < len(self.lineas) and '"' in self.lineas[indice_comentario + 1]:
                partes = self.lineas[indice_comentario + 1].split('"')
                if len(partes) > 1:
                    self.lineas[indice_comentario + 1] = f'{partes[0]}"{traduccion}"{partes[2] if len(partes) > 2 else ""}'

            with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
                f.writelines(self.lineas)

        except Exception as e:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_guardar'], f"{self.traducciones[self.idioma]['error_guardar']} {e}")

    def linea_anterior(self):
        """ Cambia a la línea anterior """
        if self.indice_linea > 0:
            self.indice_linea -= 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def linea_siguiente(self):
        """ Cambia a la línea siguiente """
        if self.indice_linea < len(self.indices_comentarios) - 1:
            self.indice_linea += 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def actualizar_botones(self):
        """ Actualiza el estado de los botones según la navegación """
        self.boton_anterior.setEnabled(self.indice_linea > 0)
        self.boton_siguiente.setEnabled(self.indice_linea < len(self.indices_comentarios) - 1)
        self.boton_guardar.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = Dorouh()
    ventana.show()
    sys.exit(app.exec_())
