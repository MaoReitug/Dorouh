import sys
import os
import io
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QHBoxLayout, QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from configs import *


class NoMasColores(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def insertFromMimeData(self, source):
        """Sobrescribe el método para pegar solo texto sin formato."""
        if source.hasText():
            self.insertPlainText(source.text())

class Dorouh(QWidget):
    def __init__(self):
        super().__init__()

        # Definir el directorio actual del archivo
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        # Establecer el ícono de la ventana y la barra de tareas
        self.setWindowIcon(QIcon(os.path.join(directorio_actual, 'icon.png')))

        # Definir el título y tamaño de la ventana
        self.setWindowTitle("Traductor v1.1")
        self.setGeometry(100, 100, 800, 600)

        # Inicialización de variables
        self.archivo_seleccionado = "Ningún archivo seleccionado"
        self.lineas = []
        self.indice_linea = 0
        self.indices_comentarios = []
        self.ruta_archivo = None
        self.idioma = idiomaX  # Idioma predeterminado (español)

        # Diccionario de traducciones para español e inglés
        self.traducciones = IDIOMAS

        self.initUI()

    def initUI(self):
        """ Configura la interfaz de usuario con los botones, etiquetas y áreas de texto """
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Variable para rastrear el estado del tema
        self.tema_oscuro = False
        
        """ Aplica el estilo con el color de fondo desde el diccionario FondoC """
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {coloresClaros['fondo']};    /* Fondo de la ventana desde FondoC */
                color: black;                             /* Texto negro */
            }}
            QLabel {{
                color: black;                             /* Texto de las etiquetas en negro */
            }}
            QLineEdit, QTextEdit {{
                background-color: #f5f5f5;                /* Gris claro para cuadros de texto */
                border: 1px solid #ccc;                   /* Borde gris claro */
                border-radius: 5px;                       /* Bordes redondeados */
                padding: 5px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid #4CAF50;                /* Borde verde cuando está en foco */
                background-color: white;                  /* Fondo blanco cuando está en foco */
            }}
        """)


        # Barra superior
        top_layout = QHBoxLayout()

        # Etiqueta para mostrar el archivo seleccionado
        self.etiqueta_archivo = QLabel(self.traducciones[self.idioma]['ningun_archivo'])
        self.etiqueta_archivo.setFont(QFont('Arial', 12, QFont.Bold))
        self.etiqueta_archivo.setAlignment(Qt.AlignLeft)
        top_layout.addWidget(self.etiqueta_archivo)

        # Botón para buscar un archivo
        self.boton_buscar = QPushButton(self.traducciones[self.idioma]['buscar_archivo'], self)
        self.boton_buscar.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_buscar.clicked.connect(self.seleccionar_archivo)
        top_layout.addWidget(self.boton_buscar)

        # Crear un layout horizontal solo para los botones de idioma y tema
        idioma_tema_layout = QHBoxLayout()
        idioma_tema_layout.setSpacing(10)  # Sin espacio entre los botones

        # Botón para cambiar idioma
        self.boton_idioma = QPushButton(self.traducciones[self.idioma][self.idioma], self)
        self.boton_idioma.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_idioma.setFixedWidth(100)
        self.boton_idioma.clicked.connect(self.cambiar_idioma)
        idioma_tema_layout.addWidget(self.boton_idioma)

        # Botón de ejemplo para cambiar de tema
        self.boton_tema = QPushButton(self.traducciones[self.idioma]['Tema'], self)
        self.boton_tema.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_tema.setFixedWidth(100)
        self.boton_tema.clicked.connect(self.cambiar_tema)
        idioma_tema_layout.addWidget(self.boton_tema)

        # Agregar el layout de idioma y tema al layout principal
        top_layout.addLayout(idioma_tema_layout)

        # Asignar el layout a tu widget principal (por ejemplo, a la ventana)
        layout.addLayout(top_layout)

        # Área para mostrar el texto seleccionado para traducir
        self.texto_seleccionable = NoMasColores(self)
        self.texto_seleccionable.setFont(QFont('Arial', 12))
        self.texto_seleccionable.setReadOnly(True)
        self.texto_seleccionable.setStyleSheet("QTextEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; height: 80px; }")
        layout.addWidget(self.texto_seleccionable)

        # Barra de búsqueda para línea
        self.buscador = QLineEdit(self)
        self.buscador.setPlaceholderText(self.traducciones[self.idioma]['buscar_linea'])
        self.buscador.setStyleSheet("QLineEdit { font-size: 14px; padding: 5px; border: 1px solid #ccc; border-radius: 5px; }")
        self.buscador.returnPressed.connect(self.buscar_por_linea)
        layout.addWidget(self.buscador)

        # Botón para copiar el texto seleccionado
        self.boton_copiar = QPushButton(self.traducciones[self.idioma]['copiar'], self)
        self.boton_copiar.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_copiar.clicked.connect(self.copiar_texto)
        layout.addWidget(self.boton_copiar)

        # Área para mostrar la traducción
        self.cuadro_traduccion = NoMasColores(self)
        self.cuadro_traduccion.setFont(QFont('Arial', 12))
        self.cuadro_traduccion.setStyleSheet("QTextEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; height: 80px; }")
        layout.addWidget(self.cuadro_traduccion)

        # Botones para navegar entre líneas y guardar traducción
        boton_layout = QHBoxLayout()

        # Botón para ir a la línea anterior
        self.boton_anterior = QPushButton(self.traducciones[self.idioma]['anterior'], self)
        self.boton_anterior.setEnabled(False)
        self.boton_anterior.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_anterior.clicked.connect(self.linea_anterior)
        boton_layout.addWidget(self.boton_anterior)

        # Botón para guardar la traducción
        self.boton_guardar = QPushButton(self.traducciones[self.idioma]['guardar'], self)
        self.boton_guardar.setEnabled(False)
        self.boton_guardar.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_guardar.clicked.connect(self.guardar_traduccion)
        boton_layout.addWidget(self.boton_guardar)

        # Botón para ir a la línea siguiente
        self.boton_siguiente = QPushButton(self.traducciones[self.idioma]['siguiente'], self)
        self.boton_siguiente.setEnabled(False)
        self.boton_siguiente.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_siguiente.clicked.connect(self.linea_siguiente)
        boton_layout.addWidget(self.boton_siguiente)
        

        # Etiqueta para mostrar el progreso de traducción
        progreso_layout = QHBoxLayout()

        self.etiqueta_progreso = QLabel("N/a")
        self.etiqueta_progreso.setFont(QFont('Arial', 12))
        self.etiqueta_progreso.setAlignment(Qt.AlignLeft)
        progreso_layout.addWidget(self.etiqueta_progreso)

        self.boton_ir_vacias = QPushButton(self.traducciones[self.idioma]['ir_a_vacias'], self)
        self.boton_ir_vacias.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_ir_vacias.clicked.connect(self.ir_a_linea_vacia)
        progreso_layout.addWidget(self.boton_ir_vacias)
        

        layout.addLayout(progreso_layout)


        layout.addLayout(boton_layout)
        self.setLayout(layout)





    def cambiar_tema(self):
            """Alterna entre tema oscuro y claro."""
            self.tema_oscuro = not self.tema_oscuro
            self.aplicar_tema()

    def aplicar_tema(self):
            """Aplica el tema actual basado en la configuración."""
            
            if self.tema_oscuro:
                tema = Config.tema_oscuro(coloresOscuros)
                self.cuadro_traduccion.setStyleSheet(f"background-color: black;")
                self.texto_seleccionable.setStyleSheet(f"background-color: black;")
                self.buscador.setStyleSheet(f"background-color: black;")
            else:
                tema = Config.tema_claro(coloresClaros)
                self.cuadro_traduccion.setStyleSheet(f"background-color: #f5f5f5;")
                self.texto_seleccionable.setStyleSheet(f"background-color: #f5f5f5;")
                self.buscador.setStyleSheet(f"background-color: #f5f5f5;")

            # Aplica los estilos al fondo y texto
            self.setStyleSheet(f"background-color: {tema['background_color']}; color: {tema['text_color']};")
            
            # Actualiza los estilos de los botones
            self.boton_buscar.setStyleSheet(tema["button_style"])
            self.boton_idioma.setStyleSheet(tema["button_style"])
            self.boton_tema.setStyleSheet(tema["button_style"])
            self.boton_copiar.setStyleSheet(tema["button_style"])
            self.boton_anterior.setStyleSheet(tema["button_style"])
            self.boton_siguiente.setStyleSheet(tema["button_style"])
            self.boton_guardar.setStyleSheet(tema["button_style"])
            self.boton_ir_vacias.setStyleSheet(tema["button_style"])



    def ir_a_linea_vacia(self):
        """Salta a la primera línea vacía detectada."""
        if not hasattr(self, 'lineas') or not self.lineas:
            QMessageBox.warning(self, self.traducciones[self.idioma]['error'], self.traducciones[self.idioma]['archivo_no_cargado'])
            return

        if self.lineas_vacias:
            linea_vacia = self.lineas_vacias[0] - 1  # Convertir a índice
            if linea_vacia in self.indices_comentarios:
                self.indice_linea = self.indices_comentarios.index(linea_vacia)
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
        else:
            QMessageBox.information(self, self.traducciones[self.idioma]['sin_lineas_vacias'], self.traducciones[self.idioma]['sin_lineas_vacias'])


    def cambiar_idioma(self):
        """ Cambia el idioma de la interfaz entre español e inglés """
        self.idioma = 'en' if self.idioma == 'es' else 'es'

        # Actualiza los textos de los botones
        self.boton_buscar.setText(self.traducciones[self.idioma]['buscar_archivo'])
        self.boton_copiar.setText(self.traducciones[self.idioma]['copiar'])
        self.boton_guardar.setText(self.traducciones[self.idioma]['guardar'])
        self.boton_anterior.setText(self.traducciones[self.idioma]['anterior'])
        self.boton_siguiente.setText(self.traducciones[self.idioma]['siguiente'])
        self.boton_siguiente
        self.boton_idioma.setText(self.traducciones[self.idioma][self.idioma])
        
        
        
        self.boton_ir_vacias.setText(self.traducciones[self.idioma]['ir_a_vacias'])
        self.boton_tema.setText(self.traducciones[self.idioma]['Tema'])
        

        # Actualiza la etiqueta del archivo seleccionado
        self.etiqueta_archivo.setText(f"{self.traducciones[self.idioma]['archivo_seleccionado']} {os.path.basename(self.ruta_archivo) if self.ruta_archivo else self.traducciones[self.idioma]['ningun_archivo']}")

        # Actualiza el texto del buscador
        self.buscador.setPlaceholderText(self.traducciones[self.idioma]['buscar_linea'])  # <-- Actualización aquí
        
        
        

    def seleccionar_archivo(self):
        """ Abre un cuadro de diálogo para seleccionar un archivo """
        archivo, _ = QFileDialog.getOpenFileName(self, self.traducciones[self.idioma]['buscar_archivo'], "", "Archivos Ren'Py (*.rpy)")
        if archivo:
            self.ruta_archivo = archivo
            self.etiqueta_archivo.setText(f"{self.traducciones[self.idioma]['archivo_seleccionado']} {os.path.basename(archivo)}")
            self.cargar_archivo(archivo)
        else:
            self.etiqueta_archivo.setText(self.traducciones[self.idioma]['ningun_archivo'])
            
    def actualizar_progreso(self):
        """Actualiza la etiqueta de progreso traducidas/total y detecta líneas vacías."""
        self.traducidas = sum(
            1 for i in self.indices_comentarios
            if i + 1 < len(self.lineas) and '"' in self.lineas[i + 1] and self.lineas[i + 1].split('"')[1].strip()
        )
        self.lineas_vacias = [
            i + 1 for i in self.indices_comentarios
            if i + 1 < len(self.lineas) and '"' in self.lineas[i + 1] and not self.lineas[i + 1].split('"')[1].strip()
        ]
        self.etiqueta_progreso.setText(f"{self.traducidas}/{len(self.indices_comentarios)}")


    def cargar_archivo(self, archivo):
        try:
            with io.open(archivo, 'r', newline='', encoding='utf-8') as f:
                self.lineas = f.readlines()

            self.indices_comentarios = [
                i for i, linea in enumerate(self.lineas)
                if ('#' in linea and '"' in linea.split('#', 1)[1]) or linea.strip().startswith('old "')
            ]
            self.indice_linea = 0

            # Contar líneas traducidas
            self.traducidas = sum(
                1 for i in self.indices_comentarios
                if i + 1 < len(self.lineas) and '"' in self.lineas[i + 1] and self.lineas[i + 1].split('"')[1].strip()
            )
            self.total_a_traducir = len(self.indices_comentarios)

            # Actualizar progreso
            self.actualizar_progreso()

            if self.indices_comentarios:
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                QMessageBox.information(self, self.traducciones[self.idioma]['no_comentarios'], self.traducciones[self.idioma]['no_comentarios'])
        except Exception as e:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_lectura'], f"{self.traducciones[self.idioma]['error_lectura']} {e}")


    def cargar_linea(self, indice):
        """ Carga una línea específica con el comentario o texto 'old' y su traducción """
        if 0 <= indice < len(self.indices_comentarios):
            indice_comentario = self.indices_comentarios[indice]
            linea_comentario = self.lineas[indice_comentario].strip()

            # Procesa la línea si es un comentario o línea old
            texto_con_numero_linea = ''
            if '#' in linea_comentario:
                comentario = linea_comentario.split('#', 1)[1].strip()
                texto_con_numero_linea = self.procesar_comentario(comentario, indice_comentario)
            elif linea_comentario.startswith('old "'):
                texto_con_numero_linea = self.procesar_old(linea_comentario, indice_comentario)

            # Actualiza el área de texto seleccionable y la traducción
            traduccion = ''
            if indice_comentario + 1 < len(self.lineas):
                linea_traduccion = self.lineas[indice_comentario + 1].strip()
                comillas_traduccion = [i for i, c in enumerate(linea_traduccion) if c == '"']
                if len(comillas_traduccion) >= 2:
                    traduccion = linea_traduccion[comillas_traduccion[0] + 1:comillas_traduccion[-1]]

            self.actualizar_texto_traducir(texto_con_numero_linea, traduccion)

    def procesar_comentario(self, comentario, indice_comentario):
        """ Procesa un comentario extraído de una línea con '#' """
        comillas = [i for i, c in enumerate(comentario) if c == '"']
        if len(comillas) >= 2:
            texto = comentario[comillas[0] + 1:comillas[-1]]
            letra = comentario[0] if comentario[0].isalpha() else ""
            return f"{indice_comentario + 1} {letra}: {texto} "
        return f"{indice_comentario + 1}: {comentario} "

    def procesar_old(self, linea_comentario, indice_comentario):
        """ Procesa una línea que comienza con 'old' """
        comillas = [i for i, c in enumerate(linea_comentario) if c == '"']
        if len(comillas) >= 2:
            texto = linea_comentario[comillas[0] + 1:comillas[-1]]
            return f"{indice_comentario + 1} old: {texto} "
        return f"{indice_comentario + 1}: {linea_comentario}"




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
        if not self.ruta_archivo:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_no_archivo'], self.traducciones[self.idioma]['error_no_archivo'])
            return

        try:
            indice_comentario = self.indices_comentarios[self.indice_linea]
            traduccion = self.cuadro_traduccion.toPlainText().strip()

            if indice_comentario + 1 < len(self.lineas) and '"' in self.lineas[indice_comentario + 1]:
                linea = self.lineas[indice_comentario + 1]
                comillas_abiertas = linea.find('"')
                comillas_cerradas = linea.rfind('"')

                if comillas_abiertas != -1 and comillas_cerradas != -1 and comillas_abiertas < comillas_cerradas:
                    contenido_actual = linea[comillas_abiertas + 1:comillas_cerradas].strip()
                    if not contenido_actual and traduccion:  # Si estaba vacío y se pone una traducción, incrementamos
                        self.traducidas += 1
                    elif contenido_actual and not traduccion:  # Si se borra la traducción, decrementamos
                        self.traducidas -= 1

                    self.lineas[indice_comentario + 1] = f'{linea[:comillas_abiertas + 1]}{traduccion}{linea[comillas_cerradas:]}'  # Actualizar la línea

            with io.open(self.ruta_archivo, 'w', newline='', encoding='utf-8') as f:
                f.writelines(self.lineas)

            self.actualizar_progreso()  # Actualizar progreso después de guardar

        except Exception as e:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_guardar'], f"{self.traducciones[self.idioma]['error_guardar']} {e}")




    def linea_anterior(self):
        """ Cambia a la línea anterior """
        self.guardar_traduccion()
        if self.indice_linea > 0:
            self.indice_linea -= 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def linea_siguiente(self):
        """ Cambia a la línea siguiente """
        self.guardar_traduccion()
        if self.indice_linea < len(self.indices_comentarios) - 1:
            self.indice_linea += 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def actualizar_botones(self):
        """ Actualiza el estado de los botones según la navegación """
        self.boton_anterior.setEnabled(self.indice_linea > 0)
        self.boton_siguiente.setEnabled(self.indice_linea < len(self.indices_comentarios) - 1)
        self.boton_guardar.setEnabled(True)

    def buscar_por_linea(self):
        """ Permite buscar por línea usando el número proporcionado en la caja de búsqueda """
        try:
            linea_buscada = int(self.buscador.text()) - 1  # Restar 1 para que coincida con el índice
            if linea_buscada in self.indices_comentarios:
                self.indice_linea = self.indices_comentarios.index(linea_buscada)
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                QMessageBox.information(self, "No encontrado", "No se encontró.")
        except ValueError:
            QMessageBox.critical(self, "Error", "Por favor, ingrese un número válido.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = Dorouh()
    ventana.show()
    sys.exit(app.exec_())
