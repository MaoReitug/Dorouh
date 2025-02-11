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
        self.setWindowTitle("Traductor v1.2")
        self.setGeometry(100, 100, 800, 600)

        # Inicialización de variables
        self.archivo_seleccionado = "Ningún archivo seleccionado"
        self.lineas = []
        self.indice_linea = 0
        self.indices_comentarios = []
        self.ruta_archivo = None
        self.idioma = idiomaX  # Idioma predeterminado (se gestiona externamente)

        # Diccionario de traducciones para español e inglés
        self.traducciones = IDIOMAS

        # Variable para rastrear el estado del tema
        self.tema_oscuro = False

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Aplica el estilo con el color de fondo desde el diccionario
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {coloresClaros['fondo']};
                color: black;
            }}
            QLabel {{
                color: black;
            }}
            QLineEdit, QTextEdit {{
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid #4CAF50;
                background-color: white;
            }}
        """)

        # Barra superior
        top_layout = QHBoxLayout()
        
        # Etiqueta para mostrar el archivo seleccionado
        self.etiqueta_archivo = QLabel(self.traducciones[self.idioma]['ningun_archivo'])
        self.etiqueta_archivo.setFont(QFont('Arial', 12, QFont.Bold))
        self.etiqueta_archivo.setAlignment(Qt.AlignLeft)
        top_layout.addWidget(self.etiqueta_archivo)

        # Botón "Recargar" para recargar el archivo desde disco
        self.boton_recargar = QPushButton(self.traducciones[self.idioma]["Recargar"], self)
        self.boton_recargar.setFixedWidth(100)
        self.boton_recargar.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_recargar.clicked.connect(self.recargar_archivo)
        top_layout.addWidget(self.boton_recargar)

        # Botón para buscar un archivo
        self.boton_buscar = QPushButton(self.traducciones[self.idioma]['buscar_archivo'], self)
        self.boton_buscar.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_buscar.clicked.connect(self.seleccionar_archivo)
        top_layout.addWidget(self.boton_buscar)

        # Layout para botones de idioma y tema (no se tocan detalles del idioma)
        idioma_tema_layout = QHBoxLayout()
        idioma_tema_layout.setSpacing(10)

        self.boton_idioma = QPushButton(self.traducciones[self.idioma][self.idioma], self)
        self.boton_idioma.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_idioma.setFixedWidth(100)
        self.boton_idioma.clicked.connect(self.cambiar_idioma)
        idioma_tema_layout.addWidget(self.boton_idioma)

        self.boton_tema = QPushButton(self.traducciones[self.idioma]['Tema'], self)
        self.boton_tema.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_tema.setFixedWidth(100)
        self.boton_tema.clicked.connect(self.cambiar_tema)
        idioma_tema_layout.addWidget(self.boton_tema)

        top_layout.addLayout(idioma_tema_layout)
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

        # Layout de botones de navegación y auto rellenado
        boton_layout = QHBoxLayout()

        self.boton_autorellenar = QPushButton(self.traducciones[self.idioma]["Auto_Rellenar"], self)
        self.boton_autorellenar.setFixedWidth(120)
        self.boton_autorellenar.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_autorellenar.clicked.connect(self.auto_rellenar_traducciones)
        boton_layout.addWidget(self.boton_autorellenar)

        self.boton_anterior = QPushButton(self.traducciones[self.idioma]['anterior'], self)
        self.boton_anterior.setEnabled(False)
        self.boton_anterior.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_anterior.clicked.connect(self.linea_anterior)
        boton_layout.addWidget(self.boton_anterior)

        self.boton_guardar = QPushButton(self.traducciones[self.idioma]['guardar'], self)
        self.boton_guardar.setEnabled(False)
        self.boton_guardar.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_guardar.clicked.connect(self.guardar_traduccion)
        boton_layout.addWidget(self.boton_guardar)

        self.boton_siguiente = QPushButton(self.traducciones[self.idioma]['siguiente'], self)
        self.boton_siguiente.setEnabled(False)
        self.boton_siguiente.setStyleSheet(Config.boton_estilo(coloresClaros))
        self.boton_siguiente.clicked.connect(self.linea_siguiente)
        boton_layout.addWidget(self.boton_siguiente)
        
        layout.addLayout(boton_layout)

        # Layout para progreso e ir a línea vacía
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
        self.setLayout(layout)

        self.actualizar_boton_autorellenar()

    def extraer_texto_entre_comillas(self, texto):
        """Extrae el contenido entre la primera y la última comilla doble."""
        indices = [i for i, c in enumerate(texto) if c == '"']
        if len(indices) >= 2:
            return texto[indices[0] + 1:indices[-1]]
        return texto

    def cambiar_tema(self):
        """Alterna entre tema oscuro y claro."""
        self.tema_oscuro = not self.tema_oscuro
        self.aplicar_tema()

    def aplicar_tema(self):
        """Aplica el tema actual basado en la configuración."""
        if self.tema_oscuro:
            tema = Config.tema_oscuro(coloresOscuros)
            self.cuadro_traduccion.setStyleSheet("background-color: black; color: white;")
            self.texto_seleccionable.setStyleSheet("background-color: black; color: white;")
        else:
            tema = Config.tema_claro(coloresClaros)
            self.cuadro_traduccion.setStyleSheet("background-color: #f5f5f5; color: black; border: 1px solid #888;")
            self.texto_seleccionable.setStyleSheet("background-color: #f5f5f5; color: black; border: 1px solid #888;")
        self.setStyleSheet(f"background-color: {tema['background_color']}; color: {tema['text_color']};")
        self.boton_buscar.setStyleSheet(tema["button_style"])
        self.boton_idioma.setStyleSheet(tema["button_style"])
        self.boton_tema.setStyleSheet(tema["button_style"])
        self.boton_copiar.setStyleSheet(tema["button_style"])
        self.boton_anterior.setStyleSheet(tema["button_style"])
        self.boton_siguiente.setStyleSheet(tema["button_style"])
        self.boton_guardar.setStyleSheet(tema["button_style"])
        self.boton_ir_vacias.setStyleSheet(tema["button_style"])
        self.actualizar_boton_autorellenar()

    # ----------------- Método agregado para cambiar idioma -----------------
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
        self.boton_autorellenar.setText(self.traducciones[self.idioma]["Auto_Rellenar"])
        self.boton_recargar.setText(self.traducciones[self.idioma]["Recargar"])
        
        
        
        self.boton_ir_vacias.setText(self.traducciones[self.idioma]['ir_a_vacias'])
        self.boton_tema.setText(self.traducciones[self.idioma]['Tema'])
        

        # Actualiza la etiqueta del archivo seleccionado
        self.etiqueta_archivo.setText(f"{self.traducciones[self.idioma]['archivo_seleccionado']} {os.path.basename(self.ruta_archivo) if self.ruta_archivo else self.traducciones[self.idioma]['ningun_archivo']}")

        # Actualiza el texto del buscador
        self.buscador.setPlaceholderText(self.traducciones[self.idioma]['buscar_linea'])  # <-- Actualización aquí

    def recargar_archivo(self):
        """Vuelve a cargar el archivo desde disco (si se ha modificado externamente)."""
        if not self.ruta_archivo:
            QMessageBox.warning(self, "Error", "No hay archivo cargado.")
            return
        try:
            with io.open(self.ruta_archivo, 'r', newline='', encoding='utf-8') as f:
                self.lineas = f.readlines()
            # Filtrar solo líneas válidas:
            self.indices_comentarios = [
                i for i, linea in enumerate(self.lineas)
                if (linea.strip().startswith('#') and linea.count('"') >= 2)
                   or linea.strip().startswith('old "')
            ]
            self.indice_linea = 0
            self.actualizar_progreso()
            if self.indices_comentarios:
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                QMessageBox.information(self, self.traducciones[self.idioma]['no_comentarios'],
                                        self.traducciones[self.idioma]['no_comentarios'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al recargar el archivo: {e}")

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
            # Filtrar líneas válidas:
            self.indices_comentarios = [
                i for i, linea in enumerate(self.lineas)
                if (linea.strip().startswith('#') and linea.count('"') >= 2)
                   or linea.strip().startswith('old "')
            ]
            self.indice_linea = 0
            self.traducidas = sum(
                1 for i in self.indices_comentarios
                if i + 1 < len(self.lineas) and '"' in self.lineas[i + 1] and self.lineas[i + 1].split('"')[1].strip()
            )
            self.total_a_traducir = len(self.indices_comentarios)
            self.actualizar_progreso()
            self.actualizar_boton_autorellenar()
            if self.indices_comentarios:
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                QMessageBox.information(self, self.traducciones[self.idioma]['no_comentarios'],
                                        self.traducciones[self.idioma]['no_comentarios'])
        except Exception as e:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_lectura'],
                                 f"{self.traducciones[self.idioma]['error_lectura']} {e}")

    def cargar_linea(self, indice):

        if 0 <= indice < len(self.indices_comentarios):
            indice_comentario = self.indices_comentarios[indice]
            linea_comentario = self.lineas[indice_comentario].strip()

            if linea_comentario.startswith('old "'):
                texto = self.extraer_texto_entre_comillas(linea_comentario)
                texto_con_numero_linea = f"{indice_comentario + 1} old: {texto}"
            elif linea_comentario.startswith('#'):
                texto = self.extraer_texto_entre_comillas(linea_comentario)
                # Si dentro del contenido aparece otro '#' se descarta lo anterior a él
                if '#' in texto:
                    pos = texto.find('#')
                    texto = texto[pos+1:].strip()
                texto_con_numero_linea = f"{indice_comentario + 1} #: {texto}"
            else:
                texto_con_numero_linea = linea_comentario

            # La línea siguiente se asume que contiene la traducción
            traduccion = ''
            if indice_comentario + 1 < len(self.lineas):
                linea_traduccion = self.lineas[indice_comentario + 1].strip()
                comillas_traduccion = [i for i, c in enumerate(linea_traduccion) if c == '"']
                if len(comillas_traduccion) >= 2:
                    traduccion = linea_traduccion[comillas_traduccion[0] + 1:comillas_traduccion[-1]]
            self.actualizar_texto_traducir(texto_con_numero_linea, traduccion)

    def actualizar_texto_traducir(self, texto, traduccion):
        """Actualiza los cuadros de texto con la línea seleccionada y la traducción."""
        self.texto_seleccionable.setPlainText(texto)
        self.cuadro_traduccion.setPlainText(traduccion)

    def copiar_texto(self):
        """Copia el texto seleccionado al portapapeles."""
        texto = self.texto_seleccionable.toPlainText().strip()
        texto_sin_numero = texto.split(':', 1)[1].strip() if ':' in texto else texto
        QApplication.clipboard().setText(texto_sin_numero)

    def guardar_traduccion(self):
        if not self.ruta_archivo:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_no_archivo'],
                                 self.traducciones[self.idioma]['error_no_archivo'])
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
                    if not contenido_actual and traduccion:
                        self.traducidas += 1
                    elif contenido_actual and not traduccion:
                        self.traducidas -= 1
                    self.lineas[indice_comentario + 1] = f'{linea[:comillas_abiertas + 1]}{traduccion}{linea[comillas_cerradas:]}'
            with io.open(self.ruta_archivo, 'w', newline='', encoding='utf-8') as f:
                f.writelines(self.lineas)
            self.actualizar_progreso()
            self.actualizar_boton_autorellenar()
        except Exception as e:
            QMessageBox.critical(self, self.traducciones[self.idioma]['error_guardar'],
                                 f"{self.traducciones[self.idioma]['error_guardar']} {e}")

    def linea_anterior(self):
        """Cambia a la línea anterior."""
        self.guardar_traduccion()
        if self.indice_linea > 0:
            self.indice_linea -= 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def linea_siguiente(self):
        """Cambia a la línea siguiente."""
        self.guardar_traduccion()
        if self.indice_linea < len(self.indices_comentarios) - 1:
            self.indice_linea += 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def actualizar_botones(self):
        """Actualiza el estado de los botones según la navegación."""
        self.boton_anterior.setEnabled(self.indice_linea > 0)
        self.boton_siguiente.setEnabled(self.indice_linea < len(self.indices_comentarios) - 1)
        self.boton_guardar.setEnabled(True)

    def buscar_por_linea(self):
        """Permite buscar por línea usando el número proporcionado en la caja de búsqueda."""
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

    # ================= Funciones de Auto Rellenado =================

    def extraer_dialogo(self, linea):

        if linea.strip().startswith('#') or linea.strip().startswith('old "'):
            return self.extraer_texto_entre_comillas(linea)
        return ""

    def obtener_traduccion(self, indice_comentario):

        if indice_comentario + 1 < len(self.lineas):
            linea = self.lineas[indice_comentario + 1]
            comillas = [i for i, c in enumerate(linea) if c == '"']
            if len(comillas) >= 2:
                return linea[comillas[0] + 1:comillas[-1]].strip()
        return ""

    def hay_autorellenar_disponible(self):

        dialogos_vistos = {}
        for idx in self.indices_comentarios:
            dialogo = self.extraer_dialogo(self.lineas[idx])
            traduccion = self.obtener_traduccion(idx)
            if dialogo in dialogos_vistos:
                if (traduccion and not dialogos_vistos[dialogo]) or (not traduccion and dialogos_vistos[dialogo]):
                    return True
            else:
                dialogos_vistos[dialogo] = bool(traduccion)
        return False

    def actualizar_boton_autorellenar(self):

        if self.hay_autorellenar_disponible():
            self.boton_autorellenar.setEnabled(True)
            style = Config.boton_estilo(coloresOscuros) if self.tema_oscuro else Config.boton_estilo(coloresClaros)
            self.boton_autorellenar.setStyleSheet(style)
        else:
            self.boton_autorellenar.setEnabled(False)
            self.boton_autorellenar.setStyleSheet("background-color: grey; color: white;")

    def auto_rellenar_traducciones(self):
        if not self.ruta_archivo:
            QMessageBox.warning(self, self.traducciones[self.idioma]['error'], "Archivo no cargado")
            return

        # Construir un diccionario: diálogo -> traducción (no vacía)
        traducciones_dict = {}
        for idx in self.indices_comentarios:
            traduccion = self.obtener_traduccion(idx)
            if traduccion:
                dialogo = self.extraer_dialogo(self.lineas[idx])
                if dialogo not in traducciones_dict:
                    traducciones_dict[dialogo] = traduccion

        auto_rellenados = 0
        lineas_actualizadas = []
        
        # Auto rellena líneas con diálogos repetidos y traducción vacía
        for idx in self.indices_comentarios:
            dialogo = self.extraer_dialogo(self.lineas[idx])
            if dialogo in traducciones_dict:
                current_traduccion = self.obtener_traduccion(idx)
                if not current_traduccion:
                    linea = self.lineas[idx + 1]
                    comillas = [i for i, c in enumerate(linea) if c == '"']
                    if len(comillas) >= 2:
                        new_translation = traducciones_dict[dialogo]
                        self.lineas[idx + 1] = f'{linea[:comillas[0] + 1]}{new_translation}{linea[comillas[-1]:]}'
                        auto_rellenados += 1
                        lineas_actualizadas.append(idx + 1)

        if auto_rellenados > 0:
            try:
                with io.open(self.ruta_archivo, 'w', newline='', encoding='utf-8') as f:
                    f.writelines(self.lineas)
            except Exception as e:
                QMessageBox.critical(self, self.traducciones[self.idioma]['error_guardar'],
                                     f"{self.traducciones[self.idioma]['error_guardar']} {e}")
            self.actualizar_progreso()
            for current_idx in lineas_actualizadas:
                if current_idx < len(self.lineas):
                    linea = self.lineas[current_idx]
                    comillas = [i for i, c in enumerate(linea) if c == '"']
                    if len(comillas) >= 2:
                        new_traduccion = linea[comillas[0] + 1:comillas[-1]].strip()
                        self.cuadro_traduccion.setPlainText(new_traduccion)
            QMessageBox.information(self, "Auto Rellenar", f"Se auto-rellenaron {auto_rellenados} traducciones.")
        else:
            QMessageBox.information(self, "Auto Rellenar", "No hay diálogos repetidos con traducción para auto rellenar.")
        self.actualizar_boton_autorellenar()

    # ---------------- Método agregado para 'ir a línea vacía' ----------------
    def ir_a_linea_vacia(self):

        if not self.lineas:
            QMessageBox.warning(self, "Error", "Archivo no cargado.")
            return
        if hasattr(self, 'lineas_vacias') and self.lineas_vacias:
            linea_vacia = self.lineas_vacias[0] - 1  # Convertir a índice
            if linea_vacia in self.indices_comentarios:
                self.indice_linea = self.indices_comentarios.index(linea_vacia)
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                QMessageBox.information(self, "Info", "No se encontró línea vacía.")
        else:
            QMessageBox.information(self, "Info", "No hay líneas vacías.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = Dorouh()
    ventana.show()
    sys.exit(app.exec_())
