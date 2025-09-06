import os
import io
import re
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from configs import idiomaX, IDIOMAS, coloresClaros, coloresOscuros, Config, cargar_preferencia_tema, guardar_preferencia_tema, cargar_preferencia_idioma, guardar_preferencia_idioma

class Dorouh(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuración del estilo ttk para una apariencia moderna
        self.style = ttk.Style(self)
        self.style.theme_use('clam')


    # Cargar preferencias de tema e idioma desde archivo
        self.tema_oscuro = self.cargar_preferencia_tema()
        self.idioma = cargar_preferencia_idioma()

        # Configuración de la ventana principal
        self.title("Traductor v2.0")
        self.geometry("800x600")
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(directorio_actual, "icon.png")
        try:
            self.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass

        # Variables internas
        self.archivo_seleccionado = "Ningún archivo seleccionado"
        self.lineas = []                  # Todas las líneas del archivo
        self.all_indices_comentarios = [] # Índices que contienen diálogos originales
        self.indices_comentarios = []     # Índices filtrados (excluyendo los descartados) para navegación
        self.indice_linea = 0             # Índice actual (posición en indices_comentarios)
        self.descartes = set()            # Conjunto de índices descartados (persistidos en archivo)
        self.ruta_archivo = None
    # self.idioma = idiomaX           # Ya se carga desde preferencias
        self.traducciones = IDIOMAS

        self.initUI()
        self.aplicar_tema()
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # Guardar preferencia de tema al cerrar
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def cargar_preferencia_tema(self):
        return cargar_preferencia_tema()

    def guardar_preferencia_tema(self):
        guardar_preferencia_tema(self.tema_oscuro)

    def on_close(self):
        self.guardar_preferencia_tema()
        guardar_preferencia_idioma(self.idioma)
        self.destroy()

    def initUI(self):
        # Frame principal con fondo y borde moderno
        self.main_frame = tk.Frame(self, padx=24, pady=24, bg="#f5f6fa", bd=2, relief="groove")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Barra superior ---
        self.top_frame = tk.Frame(self.main_frame, bg="#f5f6fa")
        self.top_frame.pack(fill=tk.X, pady=8)
        self.etiqueta_archivo = tk.Label(self.top_frame, text=self.traducciones[self.idioma]['ningun_archivo'],
                                         font=("Segoe UI", 13, "bold"), bg="#f5f6fa", fg="#222")
        self.etiqueta_archivo.pack(side=tk.LEFT, padx=(0,12))
        self.boton_recargar = ttk.Button(self.top_frame, text="⟳ " + self.traducciones[self.idioma]['Recargar'], width=12, command=self.recargar_archivo)
        self.boton_recargar.pack(side=tk.LEFT, padx=6)
        self.boton_buscar = ttk.Button(self.top_frame, text="🔍 " + self.traducciones[self.idioma]['buscar_archivo'],
                                      command=self.seleccionar_archivo)
        self.boton_buscar.pack(side=tk.LEFT, padx=6)
        self.boton_configuraciones = ttk.Button(self.top_frame, text="⚙ " + self.traducciones[self.idioma]['configuraciones'], width=15,
                            command=self.abrir_configuraciones)
        self.boton_configuraciones.pack(side=tk.RIGHT, padx=6)

        # Botón Escanear para crear cache de líneas repetidas
        self.boton_escanear = ttk.Button(self.top_frame, text="🔎 " + (self.traducciones[self.idioma]['Escanear'] if 'Escanear' in self.traducciones[self.idioma] else "Scan"), width=12, command=self.escanear_dialogos_repetidos)
        self.boton_escanear.pack(side=tk.RIGHT, padx=6)

        # --- Área de texto original ---
        self.texto_seleccionable = tk.Text(self.main_frame, height=7, wrap=tk.WORD, font=("Segoe UI", 12),
                                           bg="#e9ecef", fg="#222", relief="flat", bd=2)
        self.texto_seleccionable.config(state=tk.DISABLED)
        self.texto_seleccionable.pack(fill=tk.X, pady=(8,4), ipady=4)

        # --- Buscador ---
        buscador_frame = tk.Frame(self.main_frame, bg="#f5f6fa")
        buscador_frame.pack(fill=tk.X, pady=(0,8))
        self.buscador = ttk.Entry(buscador_frame, font=("Segoe UI", 12))
        self.buscador.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8), ipady=2)
        self.buscador.bind("<Return>", lambda event: self.buscar_por_linea())
        self.boton_copiar = ttk.Button(buscador_frame, text="📋 " + self.traducciones[self.idioma]['copiar'], command=self.copiar_texto)
        self.boton_copiar.pack(side=tk.RIGHT)

        # --- Área de traducción ---
        self.cuadro_traduccion = tk.Text(self.main_frame, height=7, wrap=tk.WORD, font=("Segoe UI", 12),
                                         bg="#e9ecef", fg="#222", relief="flat", bd=2)
        self.cuadro_traduccion.pack(fill=tk.X, pady=(4,8), ipady=4)

        # --- Botones de navegación y "Ver Líneas" ---
        self.nav_frame = tk.Frame(self.main_frame, bg="#f5f6fa")
        self.nav_frame.pack(fill=tk.X, pady=8)
        self.botones_frame = tk.Frame(self.nav_frame, bg="#f5f6fa")
        self.botones_frame.pack(expand=True, side=tk.LEFT)
        self.boton_anterior = ttk.Button(self.botones_frame, text="← " + self.traducciones[self.idioma]['anterior'], width=18,
                                        command=self.linea_anterior, state=tk.DISABLED)
        self.boton_anterior.pack(side=tk.LEFT, padx=6)
        self.boton_guardar = ttk.Button(self.botones_frame, text="💾 " + self.traducciones[self.idioma]['guardar'], width=12,
                                       command=self.guardar_traduccion, state=tk.DISABLED)
        self.boton_guardar.pack(side=tk.LEFT, padx=6)
        self.boton_siguiente = ttk.Button(self.botones_frame, text=self.traducciones[self.idioma]['siguiente'] + " →", width=18,
                                         command=self.linea_siguiente, state=tk.DISABLED)
        self.boton_siguiente.pack(side=tk.LEFT, padx=6)

        # --- Progreso y botón "Ir a Vacías" ---
        self.progress_frame = tk.Frame(self.main_frame, bg="#f5f6fa")
        self.progress_frame.pack(fill=tk.X, pady=8)
        self.etiqueta_progreso = tk.Label(self.progress_frame, text="N/a", font=("Segoe UI", 12), bg="#f5f6fa", fg="#222")
        self.etiqueta_progreso.pack(side=tk.LEFT)
        self.boton_ir_vacias = ttk.Button(self.progress_frame, text="🕳 " + self.traducciones[self.idioma]['ir_a_vacias'],
                                         command=self.ir_a_linea_vacia)
        self.boton_ir_vacias.pack(side=tk.RIGHT)
        self.boton_lista_lineas = ttk.Button(self.nav_frame, text="📄 " + (self.traducciones[self.idioma]['Ver_Lineas'] if 'Ver_Lineas' in self.traducciones[self.idioma] else "View Lines"), width=12,
                        command=self.abrir_lista_lineas)
        self.boton_lista_lineas.pack(side=tk.RIGHT, padx=6)
        self.boton_autorellenar = ttk.Button(
            self.nav_frame,
            text="✨ " + (self.traducciones[self.idioma]['Auto_Rellenar'] if 'Auto_Rellenar' in self.traducciones[self.idioma] else "Improve"),
            width=15,
            command=self.auto_rellenar_traducciones
        )
        self.boton_autorellenar.pack(side=tk.RIGHT, padx=6)

        self.actualizar_boton_autorellenar()

    def abrir_configuraciones(self):
        config_win = tk.Toplevel(self)
        config_win.title(self.traducciones[self.idioma]['configuraciones'])
        config_win.geometry("220x250")
        config_win.resizable(False, False)
        config_bg = coloresClaros['fondo'] if not self.tema_oscuro else coloresOscuros['fondo']
        config_win.configure(bg=config_bg)
        idioma_var = tk.StringVar(value=self.idioma)
        tema_var = tk.BooleanVar(value=self.tema_oscuro)

        lbl_idioma = tk.Label(config_win, text=self.traducciones[self.idioma]['es']+":", bg=config_bg, fg="black" if not self.tema_oscuro else "white")
        lbl_idioma.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        opciones_idioma = ["es", "en"]
        om_idioma = tk.OptionMenu(config_win, idioma_var, *opciones_idioma)
        om_idioma.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        lbl_tema = tk.Label(config_win, text=self.traducciones[self.idioma]['Tema']+":", bg=config_bg, fg="black" if not self.tema_oscuro else "white")
        lbl_tema.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tema_selector = tk.Checkbutton(config_win, text=self.traducciones[self.idioma]['Tema'], variable=tema_var, bg=config_bg, fg="black" if not self.tema_oscuro else "white", selectcolor=config_bg)
        tema_selector.grid(row=1, column=1, sticky="w", padx=10, pady=10)

        btn_borrar = ttk.Button(config_win, text="Borrar Cache" if self.idioma == 'es' else "Clear Cache", command=self.borrar_cache_descartes)
        btn_borrar.grid(row=2, column=0, columnspan=2, pady=10)
        btn_cerrar = ttk.Button(config_win, text="Cerrar" if self.idioma == 'es' else "Close", command=config_win.destroy)
        btn_cerrar.grid(row=3, column=0, columnspan=2, pady=10)

        def actualizar_idioma(*args):
            seleccionado = idioma_var.get()
            if seleccionado != self.idioma:
                self.cambiar_idioma_manual(seleccionado)
        idioma_var.trace("w", actualizar_idioma)

        def actualizar_tema(*args):
            self.tema_oscuro = tema_var.get()
            self.aplicar_tema()
            self.guardar_preferencia_tema()
        tema_var.trace("w", actualizar_tema)

    def aplicar_tema(self):
        # Aplica el tema usando la función de configs.py
        Config.aplicar_tema(self, oscuro=self.tema_oscuro)
        # Actualiza colores de frames y widgets
        color_fondo = coloresOscuros['fondo'] if self.tema_oscuro else coloresClaros['fondo']
        color_fg = "white" if self.tema_oscuro else "black"
        # Frames
        self.main_frame.config(bg=color_fondo)
        self.top_frame.config(bg=color_fondo)
        self.texto_seleccionable.config(bg="#2d2d2d" if self.tema_oscuro else "#d9d9d9", fg=color_fg)
        self.cuadro_traduccion.config(bg="#2d2d2d" if self.tema_oscuro else "#d9d9d9", fg=color_fg)
        self.nav_frame.config(bg=color_fondo)
        self.botones_frame.config(bg=color_fondo)
        self.progress_frame.config(bg=color_fondo)
        self.etiqueta_archivo.config(bg=color_fondo, fg=color_fg)
        self.etiqueta_progreso.config(bg=color_fondo, fg=color_fg)
        # Actualiza ventana de lista si está abierta
        for w in self.winfo_children():
            if isinstance(w, tk.Toplevel):
                w.config(bg=color_fondo)


    def cambiar_idioma_manual(self, nuevo_idioma):
        self.idioma = nuevo_idioma
        guardar_preferencia_idioma(self.idioma)
        # Actualizar todos los textos de la UI
        self.boton_buscar.config(text="🔍 " + self.traducciones[self.idioma]['buscar_archivo'])
        self.boton_copiar.config(text="📋 " + self.traducciones[self.idioma]['copiar'])
        self.boton_guardar.config(text="💾 " + self.traducciones[self.idioma]['guardar'])
        self.boton_anterior.config(text="← " + self.traducciones[self.idioma]['anterior'])
        self.boton_siguiente.config(text=self.traducciones[self.idioma]['siguiente'] + " →")
        self.boton_ir_vacias.config(text="🕳 " + self.traducciones[self.idioma]['ir_a_vacias'])
        self.boton_configuraciones.config(text="⚙ " + self.traducciones[self.idioma]['configuraciones'])
        self.boton_recargar.config(text="⟳ " + self.traducciones[self.idioma]['Recargar'])
        self.boton_escanear.config(text="🔎 " + (self.traducciones[self.idioma]['Escanear'] if 'Escanear' in self.traducciones[self.idioma] else "Scan"))
        self.boton_lista_lineas.config(text="📄 " + (self.traducciones[self.idioma]['Ver_Lineas'] if 'Ver_Lineas' in self.traducciones[self.idioma] else "View Lines"))
        self.boton_autorellenar.config(text="✨ " + (self.traducciones[self.idioma]['Auto_Rellenar'] if 'Auto_Rellenar' in self.traducciones[self.idioma] else "Improve"))
        archivo_text = os.path.basename(self.ruta_archivo) if self.ruta_archivo else self.traducciones[self.idioma]['ningun_archivo']
        self.etiqueta_archivo.config(text=f"{self.traducciones[self.idioma]['archivo_seleccionado']} {archivo_text}")
        self.buscador.delete(0, tk.END)
        self.buscador.insert(0, self.traducciones[self.idioma]['buscar_linea'])

    def cargar_archivo_en_cache(self, archivo):
        self.etiqueta_archivo.config(text="Cargando archivo...")
        def load_file():
            try:
                with io.open(archivo, 'r', newline='', encoding='utf-8') as f:
                    lineas = f.readlines()
                # Intentar cargar cache de diálogos repetidos
                cache_path = os.path.join(self.cache_dir, f"cache-dialogos-{os.path.basename(archivo)}.json")
                if os.path.exists(cache_path):
                    with open(cache_path, "r", encoding="utf-8") as fjson:
                        dialogos_json = json.load(fjson)
                    # Usar solo la primera ocurrencia de cada diálogo
                    all_indices_comentarios = [v['lineas'][0] for v in dialogos_json.values()]
                    self.dialogos_json = dialogos_json
                else:
                    # Sin cache, usar método normal
                    all_indices_comentarios = [i for i, linea in enumerate(lineas)
                        if (linea.strip().startswith('#') and linea.count('"') >= 2)
                        or linea.strip().startswith('old "')]
                    self.dialogos_json = None
                self.after(0, lambda: self.finalizar_carga(archivo, lineas, all_indices_comentarios))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Error al cargar el archivo: {e}"))
        threading.Thread(target=load_file, daemon=True).start()

    def finalizar_carga(self, archivo, lineas, all_indices_comentarios=None):
        self.lineas = lineas
        if all_indices_comentarios is not None:
            self.all_indices_comentarios = all_indices_comentarios
        else:
            self.all_indices_comentarios = [
                i for i, linea in enumerate(self.lineas)
                if (linea.strip().startswith('#') and linea.count('"') >= 2)
                or linea.strip().startswith('old "')
            ]
        self.cargar_cache_descartes()
        self.indices_comentarios = [i for i in self.all_indices_comentarios if i not in self.descartes]
        self.indice_linea = 0
        self.actualizar_progreso()
        self.actualizar_boton_autorellenar()
        if self.indices_comentarios:
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()
        else:
            messagebox.showinfo("Info", self.traducciones[self.idioma]['no_comentarios'])
        archivo_text = os.path.basename(archivo)
        self.etiqueta_archivo.config(text=f"{self.traducciones[self.idioma]['archivo_seleccionado']} {archivo_text}")
    def escanear_dialogos_repetidos(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Error", "No hay archivo cargado.")
            return
        try:
            with io.open(self.ruta_archivo, 'r', newline='', encoding='utf-8') as f:
                lineas = f.readlines()
            dialogos_json = {}
            for idx, linea in enumerate(lineas):
                if (linea.strip().startswith('#') and linea.count('"') >= 2) or linea.strip().startswith('old "'):
                    dialogo = self.extraer_dialogo(linea)
                    if dialogo:
                        if dialogo not in dialogos_json:
                            dialogos_json[dialogo] = {'lineas': [], 'traducciones': set()}
                        dialogos_json[dialogo]['lineas'].append(idx)
                        # Buscar traducción en la línea siguiente
                        if idx + 1 < len(lineas):
                            traduccion = self.extraer_texto_entre_comillas(lineas[idx + 1])
                            if traduccion:
                                dialogos_json[dialogo]['traducciones'].add(traduccion)
            # Guardar JSON provisional en carpeta cache
            cache_path = os.path.join(self.cache_dir, f"cache-dialogos-{os.path.basename(self.ruta_archivo)}.json")
            with open(cache_path, "w", encoding="utf-8") as fjson:
                json.dump({k: {'lineas': v['lineas'], 'traducciones': list(v['traducciones'])} for k, v in dialogos_json.items()}, fjson, indent=2)
            # Reflejar en el editor: solo mostrar la primera ocurrencia de cada diálogo
            self.dialogos_json = dialogos_json
            self.all_indices_comentarios = [v['lineas'][0] for v in dialogos_json.values()]
            self.cargar_cache_descartes()
            self.indices_comentarios = [i for i in self.all_indices_comentarios if i not in self.descartes]
            self.indice_linea = 0
            self.actualizar_progreso()
            self.actualizar_boton_autorellenar()
            if self.indices_comentarios:
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                messagebox.showinfo("Info", self.traducciones[self.idioma]['no_comentarios'])
            messagebox.showinfo("Cache", "Cache de diálogos repetidos generado y aplicado.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al escanear: {e}")

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(title=self.traducciones[self.idioma]['buscar_archivo'],
                                             filetypes=[("Archivos Ren'Py", "*.rpy")])
        if archivo:
            self.ruta_archivo = archivo
            self.etiqueta_archivo.config(text=f"{self.traducciones[self.idioma]['archivo_seleccionado']} {os.path.basename(archivo)}")
            self.cargar_archivo_en_cache(archivo)
        else:
            self.etiqueta_archivo.config(text=self.traducciones[self.idioma]['ningun_archivo'])

    def recargar_archivo(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Error", "No hay archivo cargado.")
            return
        self.cargar_archivo_en_cache(self.ruta_archivo)

    def obtener_cache_path(self):
        base = os.path.basename(self.ruta_archivo) if self.ruta_archivo else "default"
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), f"cache-{base}.json")

    def cargar_cache_descartes(self):
        path = self.obtener_cache_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.descartes = set(data)
            except Exception:
                self.descartes = set()
        else:
            self.descartes = set()

    def guardar_cache_descartes(self):
        path = self.obtener_cache_path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(list(self.descartes), f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el cache: {e}")

    def borrar_cache_descartes(self):
        # Borrar todos los archivos de cache en la carpeta 'cache'
        cache_dir = self.cache_dir
        borrados = 0
        if os.path.exists(cache_dir):
            for fname in os.listdir(cache_dir):
                fpath = os.path.join(cache_dir, fname)
                try:
                    if os.path.isfile(fpath):
                        os.remove(fpath)
                        borrados += 1
                except Exception:
                    pass
        # También borra el cache de descartes del archivo actual
        path = self.obtener_cache_path()
        if os.path.exists(path):
            try:
                os.remove(path)
                self.descartes = set()
            except Exception:
                pass
        self.indices_comentarios = [i for i in self.all_indices_comentarios if i not in self.descartes]
        self.indice_linea = 0
        self.actualizar_progreso()
        self.actualizar_boton_autorellenar()
        if self.indices_comentarios:
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()
        messagebox.showinfo("Cache", f"Cache borrado correctamente. Archivos eliminados: {borrados}")

    def ir_a_linea_vacia(self):
        if not self.lineas:
            messagebox.showwarning("Error", self.traducciones[self.idioma]['archivo_no_cargado'])
            return
        if hasattr(self, 'lineas_vacias') and self.lineas_vacias:
            linea_vacia = self.lineas_vacias[0] - 1
            if linea_vacia in self.indices_comentarios:
                self.indice_linea = self.indices_comentarios.index(linea_vacia)
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
        else:
            messagebox.showinfo("Info", self.traducciones[self.idioma]['sin_lineas_vacias'])

    def actualizar_progreso(self):
        self.traducidas = sum(
            1 for i in self.indices_comentarios
            if i + 1 < len(self.lineas) and '"' in self.lineas[i + 1] and self.lineas[i + 1].split('"')[1].strip()
        )
        self.lineas_vacias = [
            i + 1 for i in self.indices_comentarios
            if i + 1 < len(self.lineas) and '"' in self.lineas[i + 1] and not self.lineas[i + 1].split('"')[1].strip()
        ]
        self.etiqueta_progreso.config(text=f"{self.traducidas}/{len(self.indices_comentarios)}")

    def cargar_linea(self, indice):
        if 0 <= indice < len(self.indices_comentarios):
            indice_comentario = self.indices_comentarios[indice]
            linea_comentario = self.lineas[indice_comentario].strip()
            if linea_comentario.startswith('old "'):
                texto = self.extraer_texto_entre_comillas(linea_comentario)
                texto_con_numero_linea = f"{indice_comentario + 1} old: {texto}"
            elif linea_comentario.startswith('#'):
                match = re.match(r'^#\s*(\S+)\s*"([^"]*)"', linea_comentario)
                if match:
                    speaker = match.group(1)
                    dialogue = match.group(2)
                    texto_con_numero_linea = f"{indice_comentario + 1} [{speaker}]: {dialogue}"
                else:
                    texto = self.extraer_texto_entre_comillas(linea_comentario)
                    if '#' in texto:
                        pos = texto.find('#')
                        texto = texto[pos+1:].strip()
                    texto_con_numero_linea = f"{indice_comentario + 1}: {texto}"
            else:
                texto_con_numero_linea = linea_comentario
            traduccion = ""
            if indice_comentario + 1 < len(self.lineas):
                linea_traduccion = self.lineas[indice_comentario + 1].strip()
                traduccion = self.extraer_texto_entre_comillas(linea_traduccion)
            self.actualizar_texto_traducir(texto_con_numero_linea, traduccion)

    def extraer_texto_entre_comillas(self, texto):
        indices = [i for i, c in enumerate(texto) if c == '"']
        if len(indices) >= 2:
            return texto[indices[0] + 1:indices[-1]]
        return texto

    def actualizar_texto_traducir(self, texto, traduccion):
        self.texto_seleccionable.config(state=tk.NORMAL)
        self.texto_seleccionable.delete("1.0", tk.END)
        self.texto_seleccionable.insert(tk.END, texto)
        self.texto_seleccionable.config(state=tk.DISABLED)
        self.cuadro_traduccion.delete("1.0", tk.END)
        self.cuadro_traduccion.insert(tk.END, traduccion)

    def copiar_texto(self):
        texto = self.texto_seleccionable.get("1.0", tk.END).strip()
        if ':' in texto:
            texto_sin_numero = texto.split(':', 1)[1].strip()
        else:
            texto_sin_numero = texto
        self.clipboard_clear()
        self.clipboard_append(texto_sin_numero)

    def guardar_traduccion(self):
        if not self.ruta_archivo:
            messagebox.showerror("Error", self.traducciones[self.idioma]['error_no_archivo'])
            return
        try:
            indice_comentario = self.indices_comentarios[self.indice_linea]
            traduccion = self.cuadro_traduccion.get("1.0", tk.END).strip()
            # Obtener el diálogo actual
            dialogo_actual = self.extraer_dialogo(self.lineas[indice_comentario])
            # Si existe el cache y el diálogo está agrupado, aplicar a todas las repeticiones
            if dialogo_actual and self.dialogos_json and dialogo_actual in self.dialogos_json:
                for idx in self.dialogos_json[dialogo_actual]['lineas']:
                    if idx + 1 < len(self.lineas) and '"' in self.lineas[idx + 1]:
                        linea = self.lineas[idx + 1]
                        comillas_abiertas = linea.find('"')
                        comillas_cerradas = linea.rfind('"')
                        if comillas_abiertas != -1 and comillas_cerradas != -1 and comillas_abiertas < comillas_cerradas:
                            self.lineas[idx + 1] = f'{linea[:comillas_abiertas + 1]}{traduccion}{linea[comillas_cerradas:]}'
            else:
                # Fallback: solo la línea actual
                if indice_comentario + 1 < len(self.lineas) and '"' in self.lineas[indice_comentario + 1]:
                    linea = self.lineas[indice_comentario + 1]
                    comillas_abiertas = linea.find('"')
                    comillas_cerradas = linea.rfind('"')
                    if comillas_abiertas != -1 and comillas_cerradas != -1 and comillas_abiertas < comillas_cerradas:
                        self.lineas[indice_comentario + 1] = f'{linea[:comillas_abiertas + 1]}{traduccion}{linea[comillas_cerradas:]}'
            with io.open(self.ruta_archivo, 'w', newline='', encoding='utf-8') as f:
                f.writelines(self.lineas)
            self.actualizar_progreso()
            self.actualizar_boton_autorellenar()
            # Actualizar el cache de diálogos repetidos
            self.actualizar_cache_dialogos()
            # Mensaje visual de confirmación
            self.etiqueta_progreso.config(text=f"{self.traducidas}/{len(self.indices_comentarios)} ✔️ Guardado")
            self.after(1200, lambda: self.etiqueta_progreso.config(text=f"{self.traducidas}/{len(self.indices_comentarios)}"))
        except Exception as e:
            messagebox.showerror("Error", f"{self.traducciones[self.idioma]['error_guardar']} {e}")
    def actualizar_cache_dialogos(self):
        """Actualiza el cache JSON de diálogos repetidos para mantenerlo sincronizado con el archivo."""
        if not self.ruta_archivo:
            return
        try:
            with io.open(self.ruta_archivo, 'r', newline='', encoding='utf-8') as f:
                lineas = f.readlines()
            dialogos_json = {}
            for idx, linea in enumerate(lineas):
                if (linea.strip().startswith('#') and linea.count('"') >= 2) or linea.strip().startswith('old "'):
                    dialogo = self.extraer_dialogo(linea)
                    if dialogo:
                        if dialogo not in dialogos_json:
                            dialogos_json[dialogo] = {'lineas': [], 'traducciones': set()}
                        dialogos_json[dialogo]['lineas'].append(idx)
                        # Buscar traducción en la línea siguiente
                        if idx + 1 < len(lineas):
                            traduccion = self.extraer_texto_entre_comillas(lineas[idx + 1])
                            if traduccion:
                                dialogos_json[dialogo]['traducciones'].add(traduccion)
            # Guardar JSON provisional en carpeta cache
            cache_path = os.path.join(self.cache_dir, f"cache-dialogos-{os.path.basename(self.ruta_archivo)}.json")
            with open(cache_path, "w", encoding="utf-8") as fjson:
                json.dump({k: {'lineas': v['lineas'], 'traducciones': list(v['traducciones'])} for k, v in dialogos_json.items()}, fjson, indent=2)
        except Exception:
            pass

    def linea_anterior(self):
        self.guardar_traduccion()
        if self.indice_linea > 0:
            self.indice_linea -= 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def linea_siguiente(self):
        self.guardar_traduccion()
        if self.indice_linea < len(self.indices_comentarios) - 1:
            self.indice_linea += 1
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()

    def actualizar_botones(self):
        self.boton_anterior.config(state=tk.NORMAL if self.indice_linea > 0 else tk.DISABLED)
        self.boton_siguiente.config(state=tk.NORMAL if self.indice_linea < len(self.indices_comentarios) - 1 else tk.DISABLED)
        self.boton_guardar.config(state=tk.NORMAL)

    def buscar_por_linea(self):
        try:
            linea_buscada = int(self.buscador.get()) - 1
            if linea_buscada in self.indices_comentarios:
                self.indice_linea = self.indices_comentarios.index(linea_buscada)
                self.cargar_linea(self.indice_linea)
                self.actualizar_botones()
            else:
                messagebox.showinfo("No encontrado", "No se encontró.")
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número válido.")

    def extraer_dialogo(self, linea):
        if linea.strip().startswith('#') or linea.strip().startswith('old "'):
            return self.extraer_texto_entre_comillas(linea)
        return ""

    def obtener_traduccion(self, indice_comentario):
        if indice_comentario + 1 < len(self.lineas):
            linea = self.lineas[indice_comentario + 1]
            return self.extraer_texto_entre_comillas(linea).strip()
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
        self.boton_autorellenar.config(state=tk.NORMAL)

    def auto_rellenar_traducciones(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Error", "Archivo no cargado")
            return
        # Siempre escanear el archivo original para mostrar y editar repeticiones
        dialogos = {}
        try:
            with io.open(self.ruta_archivo, 'r', newline='', encoding='utf-8') as f:
                lineas = f.readlines()
            for idx, linea in enumerate(lineas):
                if (linea.strip().startswith('#') and linea.count('"') >= 2) or linea.strip().startswith('old "'):
                    texto = self.extraer_dialogo(linea)
                    if texto:
                        if texto not in dialogos:
                            dialogos[texto] = {'lineas': [], 'traducciones': set()}
                        dialogos[texto]['lineas'].append(idx)
                        # Buscar traducción en la línea siguiente
                        if idx + 1 < len(lineas):
                            traduccion = self.extraer_texto_entre_comillas(lineas[idx + 1])
                            if traduccion:
                                dialogos[texto]['traducciones'].add(traduccion)
        except Exception as e:
            messagebox.showerror("Error", f"Error al escanear repeticiones: {e}")


        # Ventana de gestión avanzada
        win = tk.Toplevel(self)
        win.title("Gestión de diálogos repetidos")
        win.geometry("900x600")
        win.config(bg="#f5f6fa")

        tree = ttk.Treeview(win, columns=("Dialogo", "Lineas", "Traducciones"), show="headings")
        tree.heading("Dialogo", text="Diálogo")
        tree.heading("Lineas", text="Líneas")
        tree.heading("Traducciones", text="Traducciones")
        tree.column("Dialogo", width=350)
        tree.column("Lineas", width=120)
        tree.column("Traducciones", width=300)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Insertar filas
        for texto, info in dialogos.items():
            if len(info['traducciones']) > 1:
                lineas_str = ", ".join(str(l+1) for l in info['lineas'])
                traducciones_str = ", ".join(info['traducciones'])
                tree.insert("", "end", iid=texto, values=(texto, lineas_str, traducciones_str))

        # Panel de edición
        frame_edicion = tk.Frame(win, bg="#f5f6fa")
        frame_edicion.pack(fill=tk.X, padx=10, pady=10)
        lbl = tk.Label(frame_edicion, text="Selecciona un diálogo para editar sus traducciones:", bg="#f5f6fa", font=("Segoe UI", 11))
        lbl.pack(anchor="w")
        txt_dialogo = tk.Text(frame_edicion, height=2, font=("Segoe UI", 11), state=tk.DISABLED)
        txt_dialogo.pack(fill=tk.X, pady=4)
        from tkinter import StringVar
        trad_var = StringVar()
        combo_trads = ttk.Combobox(frame_edicion, textvariable=trad_var, font=("Segoe UI", 11), state="readonly")
        combo_trads.pack(fill=tk.X, pady=4)

        # Cuadro para traducción personalizada
        lbl_perso = tk.Label(frame_edicion, text="O escribe una traducción personalizada:", bg="#f5f6fa", font=("Segoe UI", 10))
        lbl_perso.pack(anchor="w", pady=(8,0))
        entry_perso = tk.Entry(frame_edicion, font=("Segoe UI", 11))
        entry_perso.pack(fill=tk.X, pady=(0,6))

        btn_aplicar = ttk.Button(frame_edicion, text="Aplicar traducción a todas las líneas", state=tk.DISABLED)
        btn_aplicar.pack(pady=4)

        seleccion_actual = {'dialogo': None, 'lineas': [], 'traduccion': None}

        def on_select(event):
            sel = tree.focus()
            if not sel:
                return
            info = dialogos[sel]
            seleccion_actual['dialogo'] = sel
            seleccion_actual['lineas'] = info['lineas']
            txt_dialogo.config(state=tk.NORMAL)
            txt_dialogo.delete("1.0", tk.END)
            txt_dialogo.insert(tk.END, sel)
            txt_dialogo.config(state=tk.DISABLED)
            combo_trads['values'] = list(info['traducciones']) if info['traducciones'] else [""]
            if info['traducciones']:
                trad_var.set(list(info['traducciones'])[0])
            else:
                trad_var.set("")
            entry_perso.delete(0, tk.END)
            btn_aplicar.config(state=tk.NORMAL)

        tree.bind("<<TreeviewSelect>>", on_select)

        def aplicar_traduccion():
            trad = trad_var.get().strip()
            trad_perso = entry_perso.get().strip()
            if trad_perso:
                trad = trad_perso
            if not trad:
                messagebox.showwarning("Advertencia", "Debes elegir o escribir una traducción.")
                return
            for idx in seleccion_actual['lineas']:
                if idx + 1 < len(self.lineas):
                    linea = self.lineas[idx + 1]
                    comillas = [i for i, c in enumerate(linea) if c == '"']
                    if len(comillas) >= 2:
                        self.lineas[idx + 1] = f'{linea[:comillas[0] + 1]}{trad}{linea[comillas[-1]:]}'
            with io.open(self.ruta_archivo, 'w', newline='', encoding='utf-8') as f:
                f.writelines(self.lineas)
            self.actualizar_progreso()
            self.actualizar_boton_autorellenar()
            # Eliminar la fila del Treeview tras aplicar la corrección
            tree.delete(seleccion_actual['dialogo'])
            # Limpiar los cuadros y deshabilitar el botón para evitar reescrituras accidentales
            combo_trads.set("")
            entry_perso.delete(0, tk.END)
            btn_aplicar.config(state=tk.DISABLED)

        btn_aplicar.config(command=aplicar_traduccion)

    # ---------- Ventana de listado de líneas con Treeview ----------
    def abrir_lista_lineas(self):
        top = tk.Toplevel(self)
        top.title(self.traducciones[self.idioma]['Ver_Lineas'] if 'Ver_Lineas' in self.traducciones[self.idioma] else "List of Lines")
        top.geometry("1000x800")
        top.config(bg=coloresClaros.get('fondo', 'white'))
        # Crear Treeview con scrollbars (vertical y horizontal)
        tree_frame = tk.Frame(top)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        columns = ("Linea", "Dialogo", "Traduccion")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side=tk.RIGHT, fill="y")
        hsb.pack(side=tk.BOTTOM, fill="x")
        tree.pack(fill=tk.BOTH, expand=True)
        tree.heading("Linea", text=self.traducciones[self.idioma]['Linea'] if 'Linea' in self.traducciones[self.idioma] else "Line")
        tree.heading("Dialogo", text=self.traducciones[self.idioma]['Dialogo'] if 'Dialogo' in self.traducciones[self.idioma] else "Dialogue")
        tree.heading("Traduccion", text=self.traducciones[self.idioma]['Traduccion'] if 'Traduccion' in self.traducciones[self.idioma] else "Translation")
        tree.column("Linea", width=60, anchor="center")
        tree.column("Dialogo", width=400, anchor="w")
        tree.column("Traduccion", width=300, anchor="w")
        # Insertar filas: se recorren TODOS los índices (completos) para mostrarlos en la lista
        for idx in self.all_indices_comentarios:
            linea_num = idx + 1
            dialogo = self.extraer_dialogo(self.lineas[idx])
            traduccion = self.obtener_traduccion(idx)
            decoration = "+" if traduccion else "–"
            tree.insert("", "end", iid=str(idx), values=(linea_num, dialogo, f"{decoration} {traduccion}" if traduccion else f"{decoration}"))
            # Si la línea está descartada, se marca con la etiqueta
            if idx in self.descartes:
                tree.item(str(idx), tags=("descartado",))
        tree.tag_configure("descartado", background="lightcoral")
        
        # Función para detectar clic derecho en una línea (toggle descartado)
        def on_right_click(event):
            item = tree.identify_row(event.y)
            if item:
                idx = int(item)
                if idx in self.descartes:
                    # Si ya está descartada, se quita del conjunto
                    self.descartes.remove(idx)
                    tree.item(item, tags=())
                else:
                    self.descartes.add(idx)
                    tree.item(item, tags=("descartado",))
                # Actualizamos la lista filtrada (para navegación) y el cache
                self.indices_comentarios = [i for i in self.all_indices_comentarios if i not in self.descartes]
                self.guardar_cache_descartes()
                self.actualizar_progreso()
                self.actualizar_botones()
        tree.bind("<Button-3>", on_right_click)
        
        # Función para doble clic izquierdo: cargar la línea en el editor.
        def on_double_click(event):
            item = tree.identify_row(event.y)
            if item:
                abs_index = int(item)
                # Si la línea estaba descartada, se reactiva
                if abs_index in self.descartes:
                    self.descartes.remove(abs_index)
                    tree.item(item, tags=())
                    self.indices_comentarios = [i for i in self.all_indices_comentarios if i not in self.descartes]
                    self.guardar_cache_descartes()
                if abs_index in self.indices_comentarios:
                    pos = self.indices_comentarios.index(abs_index)
                    self.indice_linea = pos
                    self.cargar_linea(self.indice_linea)
                    self.actualizar_botones()
        tree.bind("<Double-1>", on_double_click)

    # (Opcional, se deja el método antiguo en caso de que se quiera usar la versión con Frames)
    def ir_desde_lista(self, idx, win):
        if idx in self.indices_comentarios:
            pos = self.indices_comentarios.index(idx)
            self.indice_linea = pos
            self.cargar_linea(self.indice_linea)
            self.actualizar_botones()
        win.destroy()

    def descartar_linea(self, idx, frame_item):
        if idx in self.indices_comentarios:
            self.indices_comentarios.remove(idx)
            self.descartes.add(idx)
            self.guardar_cache_descartes()
            if self.indice_linea >= len(self.indices_comentarios):
                self.indice_linea = max(0, len(self.indices_comentarios) - 1)
            self.actualizar_progreso()
            self.actualizar_botones()
        frame_item.destroy()

if __name__ == '__main__':
    app = Dorouh()
    app.mainloop()
