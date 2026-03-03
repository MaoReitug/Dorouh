import os
import io
import json
import shutil
import sys
import threading
import tkinter as tk
import ctypes
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import ttk
from configs import IDIOMAS, coloresClaros, coloresOscuros, Config, cargar_preferencia_tema, guardar_preferencia_tema, cargar_preferencia_idioma, guardar_preferencia_idioma, cargar_preferencia_backup, guardar_preferencia_backup

if sys.platform.startswith("win"):
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Dorouh.Translator.v3")
    except Exception:
        pass

class Dorouh(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuración del estilo ttk para una apariencia moderna
        self.style = ttk.Style(self)
        self.style.theme_use('clam')


    # Cargar preferencias de tema e idioma desde archivo
        self.tema_oscuro = self.cargar_preferencia_tema()
        self.idioma = cargar_preferencia_idioma()
        self.backup_habilitado = cargar_preferencia_backup()

        # Configuración de la ventana principal
        self.title("Traductor v3.0")
        self.geometry("980x720")
        self.minsize(900, 620)
        self._configurar_icono_aplicacion()

        # Estado mínimo para UI visual
        self.ruta_archivo = None
        self.indice_linea = 0
        self.total_lineas = 0
        self.lineas = []
        self.all_indices_comentarios = []
        self.indices_comentarios = []
        self.dialogos_json = None
        self._carga_token = 0
        self.auto_guardar_nav_var = tk.BooleanVar(value=False)
        self.guardar_duplicadas_var = tk.BooleanVar(value=False)
        self.historial_cambios = []
        self.max_historial_cambios = 100
        self._historial_seq = 0
        self.traducciones = IDIOMAS
        self.palette = self._palette()
        self._configurar_estilos_ttk()
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.backups_root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        os.makedirs(self.backups_root_dir, exist_ok=True)

        self.initUI()
        self.aplicar_tema()

        # Guardar preferencia de tema al cerrar
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def cargar_preferencia_tema(self):
        return cargar_preferencia_tema()

    def guardar_preferencia_tema(self):
        guardar_preferencia_tema(self.tema_oscuro)

    def on_close(self):
        self.guardar_preferencia_tema()
        guardar_preferencia_idioma(self.idioma)
        guardar_preferencia_backup(self.backup_habilitado)
        self.destroy()

    def tr(self, key, fallback):
        return self.traducciones.get(self.idioma, {}).get(key, fallback)

    def _configurar_icono_aplicacion(self):
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        icono_ico = os.path.join(directorio_actual, "icon.ico")
        icono_png = os.path.join(directorio_actual, "icon.png")

        if sys.platform.startswith("win"):
            if os.path.exists(icono_ico):
                try:
                    self.iconbitmap(default=icono_ico)
                except Exception:
                    pass

        if os.path.exists(icono_png):
            try:
                self.iconphoto(False, tk.PhotoImage(file=icono_png))
            except Exception:
                pass

    def _palette(self):
        if self.tema_oscuro:
            return {
                "bg": coloresOscuros['fondo'],
                "panel": "#262626",
                "surface": "#2d2d2d",
                "text": "#f2f2f2",
                "muted": "#d0d0d0",
                "border": "#3a3a3a",
                "accent": coloresOscuros['boton'],
                "accent_hover": coloresOscuros['botonb'],
            }
        return {
            "bg": coloresClaros['fondo'],
            "panel": "#edf1f5",
            "surface": "#f7f9fb",
            "text": "#26323c",
            "muted": "#5e6875",
            "border": "#cfd7e1",
            "accent": coloresClaros['boton'],
            "accent_hover": coloresClaros['botonb'],
        }

    def _configurar_estilos_ttk(self):
        p = self.palette
        self.style.configure("App.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 7))
        self.style.map("App.TButton", background=[("active", p["accent_hover"])])

        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        self.style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(10, 7))
        self.style.configure("Ghost.TButton", font=("Segoe UI", 10), padding=(8, 6))
        self.style.configure("App.TEntry", padding=6)

    def initUI(self):
        p = self.palette
        self.main_frame = tk.Frame(
            self,
            padx=24,
            pady=22,
            bg=p["panel"],
            bd=1,
            relief="solid",
            highlightbackground=p["border"],
            highlightthickness=1,
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.top_frame = tk.Frame(self.main_frame, bg=p["panel"])
        self.top_frame.pack(fill=tk.X, pady=(0, 10))

        self.etiqueta_archivo = tk.Label(
            self.top_frame,
            text=self.tr("ningun_archivo", "Ningún archivo seleccionado"),
            font=("Segoe UI", 13, "bold"),
            bg=p["panel"],
            fg=p["text"],
        )
        self.etiqueta_archivo.pack(side=tk.LEFT, padx=(0, 12))

        self.boton_recargar = ttk.Button(
            self.top_frame,
            text="⟳ " + self.tr("Recargar", "Recargar"),
            width=12,
            style="Ghost.TButton",
            command=self.recargar_archivo,
        )
        self.boton_recargar.pack(side=tk.LEFT, padx=6)

        self.boton_buscar = ttk.Button(
            self.top_frame,
            text="🔍 " + self.tr("buscar_archivo", "Buscar archivo"),
            style="Primary.TButton",
            command=self.seleccionar_archivo,
        )
        self.boton_buscar.pack(side=tk.LEFT, padx=6)

        self.boton_backups = ttk.Button(
            self.top_frame,
            text="🗂 " + self.tr("Backups", "Backups"),
            width=12,
            style="Ghost.TButton",
            command=self.abrir_ventana_backups,
        )
        self.boton_backups.pack(side=tk.LEFT, padx=6)

        self.boton_configuraciones = ttk.Button(
            self.top_frame,
            text="⚙ " + self.tr("configuraciones", "Configuraciones"),
            width=15,
            style="Secondary.TButton",
            command=self.abrir_configuraciones,
        )
        self.boton_configuraciones.pack(side=tk.RIGHT, padx=6)

        self.lbl_origen = tk.Label(
            self.main_frame,
            text=self.tr("Dialogo", "Diálogo"),
            font=("Segoe UI", 10, "bold"),
            bg=p["panel"],
            fg=p["muted"],
        )
        self.lbl_origen.pack(anchor="w", pady=(2, 4))

        self.texto_seleccionable = tk.Text(
            self.main_frame,
            height=7,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            bg=p["surface"],
            fg=p["text"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=p["border"],
            insertbackground=p["text"],
        )
        self.texto_seleccionable.insert("1.0", self.tr("placeholder_texto_original", "[Texto original]"))
        self.texto_seleccionable.config(state=tk.DISABLED)
        self.texto_seleccionable.pack(fill=tk.X, pady=(0, 8), ipady=7)

        buscador_frame = tk.Frame(self.main_frame, bg=p["panel"])
        buscador_frame.pack(fill=tk.X, pady=(0, 8))

        self.buscador = ttk.Entry(buscador_frame, font=("Segoe UI", 11), style="App.TEntry")
        self.buscador.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=2)
        self.buscador.bind("<Return>", lambda event: self.buscar_por_linea())
        self.buscador.insert(0, self.tr("buscar_linea", "Buscar línea"))

        self.boton_copiar = ttk.Button(
            buscador_frame,
            text="📋 " + self.tr("copiar", "Copiar"),
            style="Secondary.TButton",
            command=self.copiar_texto,
        )
        self.boton_copiar.pack(side=tk.RIGHT)

        self.lbl_trad = tk.Label(
            self.main_frame,
            text=self.tr("Traduccion", "Traducción"),
            font=("Segoe UI", 10, "bold"),
            bg=p["panel"],
            fg=p["muted"],
        )
        self.lbl_trad.pack(anchor="w", pady=(2, 4))

        self.cuadro_traduccion = tk.Text(
            self.main_frame,
            height=7,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            bg=p["surface"],
            fg=p["text"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=p["border"],
            insertbackground=p["text"],
        )
        self.cuadro_traduccion.insert("1.0", self.tr("placeholder_traduccion", "[Traducción]"))
        self.cuadro_traduccion.pack(fill=tk.X, pady=(0, 10), ipady=7)

        self.nav_frame = tk.Frame(self.main_frame, bg=p["panel"])
        self.nav_frame.pack(fill=tk.X, pady=8)

        self.botones_frame = tk.Frame(self.nav_frame, bg=p["panel"])
        self.botones_frame.pack(expand=True, side=tk.LEFT)

        self.nav_buttons_row = tk.Frame(self.botones_frame, bg=p["panel"])
        self.nav_buttons_row.pack(anchor="center")

        self.boton_anterior = ttk.Button(
            self.nav_buttons_row,
            text="← " + self.tr("anterior", "Anterior"),
            width=18,
            style="Secondary.TButton",
            command=self.linea_anterior,
        )
        self.boton_anterior.pack(side=tk.LEFT, padx=6)

        self.boton_guardar = ttk.Button(
            self.nav_buttons_row,
            text="💾 " + self.tr("guardar", "Guardar"),
            width=12,
            style="Primary.TButton",
            command=self.guardar_traduccion,
        )
        self.boton_guardar.pack(side=tk.LEFT, padx=6)

        self.boton_siguiente = ttk.Button(
            self.nav_buttons_row,
            text=self.tr("siguiente", "Siguiente") + " →",
            width=18,
            style="Secondary.TButton",
            command=self.linea_siguiente,
        )
        self.boton_siguiente.pack(side=tk.LEFT, padx=6)

        self.check_autoguardar_nav = ttk.Checkbutton(
            self.botones_frame,
            text="✓ " + self.tr("auto_guardar_nav", "Auto-guardar al navegar"),
            variable=self.auto_guardar_nav_var,
        )
        self.check_autoguardar_nav.pack(anchor="center", pady=(8, 0))

        self.check_guardar_duplicadas = ttk.Checkbutton(
            self.botones_frame,
            text="✓ " + self.tr("guardar_en_duplicadas", "Guardar en duplicadas"),
            variable=self.guardar_duplicadas_var,
        )
        self.check_guardar_duplicadas.pack(anchor="center", pady=(4, 0))

        self.progress_frame = tk.Frame(self.main_frame, bg=p["panel"])
        self.progress_frame.pack(fill=tk.X, pady=8)

        self.etiqueta_progreso = tk.Label(
            self.progress_frame,
            text="0/0",
            font=("Segoe UI", 11, "bold"),
            bg=p["panel"],
            fg=p["text"],
        )
        self.etiqueta_progreso.pack(side=tk.LEFT)

        self.boton_ir_vacias = ttk.Button(
            self.progress_frame,
            text="🕳 " + self.tr("ir_a_vacias", "Ir a vacías"),
            style="Ghost.TButton",
            command=self.ir_a_linea_vacia,
        )
        self.boton_ir_vacias.pack(side=tk.RIGHT)

        self.boton_lista_lineas = ttk.Button(
            self.nav_frame,
            text="📄 " + self.tr("Ver_Lineas", "Ver líneas"),
            width=12,
            style="Ghost.TButton",
            command=self.abrir_lista_lineas,
        )
        self.boton_lista_lineas.pack(side=tk.RIGHT, padx=6)

        self.boton_autorellenar = ttk.Button(
            self.nav_frame,
            text="✨ " + self.tr("Auto_Rellenar", "Auto Rellenar"),
            width=15,
            style="Ghost.TButton",
            command=self.auto_rellenar_traducciones,
        )
        self.boton_autorellenar.pack(side=tk.RIGHT, padx=6)

        self.actualizar_boton_autorellenar()

    def borrar_cache(self):
        borrados = 0
        errores = 0

        if os.path.isdir(self.cache_dir):
            for nombre in os.listdir(self.cache_dir):
                ruta = os.path.join(self.cache_dir, nombre)
                if not os.path.isfile(ruta):
                    continue
                try:
                    os.remove(ruta)
                    borrados += 1
                except Exception:
                    errores += 1

        self.dialogos_json = None

        if errores:
            messagebox.showwarning(
                self.tr("advertencia", "Advertencia"),
                f"{self.tr('Borrar_Cache', 'Borrar Cache')}: {borrados} OK, {errores} con error.",
            )
            return

        messagebox.showinfo(
            self.tr("info", "Info"),
            f"{self.tr('Borrar_Cache', 'Borrar Cache')}: {borrados} {self.tr('archivos_eliminados', 'archivos eliminados')}",
        )

    def borrar_backups(self):
        borrados = 0
        errores = 0

        if os.path.isdir(self.backups_root_dir):
            for raiz, _dirs, archivos in os.walk(self.backups_root_dir):
                for nombre in archivos:
                    ruta = os.path.join(raiz, nombre)
                    try:
                        os.remove(ruta)
                        borrados += 1
                    except Exception:
                        errores += 1

            for raiz, dirs, _archivos in os.walk(self.backups_root_dir, topdown=False):
                for nombre_dir in dirs:
                    ruta_dir = os.path.join(raiz, nombre_dir)
                    try:
                        if not os.listdir(ruta_dir):
                            os.rmdir(ruta_dir)
                    except Exception:
                        pass

        if errores:
            messagebox.showwarning(
                self.tr("advertencia", "Advertencia"),
                f"{self.tr('Borrar_Backups', 'Borrar Backups')}: {borrados} OK, {errores} con error.",
            )
            return

        messagebox.showinfo(
            self.tr("info", "Info"),
            f"{self.tr('Borrar_Backups', 'Borrar Backups')}: {borrados} {self.tr('archivos_eliminados', 'archivos eliminados')}",
        )

    def abrir_configuraciones(self):
        config_win = tk.Toplevel(self)
        config_win.title(self.tr("configuraciones", "Configuraciones"))
        config_win.geometry("300x320")
        config_win.resizable(False, False)
        config_bg = coloresClaros['fondo'] if not self.tema_oscuro else coloresOscuros['fondo']
        config_win.configure(bg=config_bg)

        estado = {"actualizando_idioma": False}

        def idioma_codigo_a_nombre():
            return {
                "es": self.tr("es", "Español"),
                "en": self.tr("en", "Inglés"),
            }

        def idioma_nombre_a_codigo(nombre):
            mapa = idioma_codigo_a_nombre()
            for codigo, etiqueta in mapa.items():
                if etiqueta == nombre:
                    return codigo
            return self.idioma

        idioma_var = tk.StringVar()
        tema_var = tk.BooleanVar(value=self.tema_oscuro)
        backup_var = tk.BooleanVar(value=self.backup_habilitado)

        lbl_idioma = tk.Label(config_win, text=self.tr("Idioma", "Idioma")+":", bg=config_bg, fg="black" if not self.tema_oscuro else "white")
        lbl_idioma.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        opciones_iniciales = list(idioma_codigo_a_nombre().values())
        idioma_var.set(idioma_codigo_a_nombre().get(self.idioma, self.idioma))
        om_idioma = tk.OptionMenu(config_win, idioma_var, *opciones_iniciales)
        om_idioma.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        lbl_tema = tk.Label(config_win, text=self.tr("Tema", "Tema")+":", bg=config_bg, fg="black" if not self.tema_oscuro else "white")
        lbl_tema.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tema_selector = tk.Checkbutton(config_win, text=self.tr("Tema", "Tema"), variable=tema_var, bg=config_bg, fg="black" if not self.tema_oscuro else "white", selectcolor=config_bg)
        tema_selector.grid(row=1, column=1, sticky="w", padx=10, pady=10)

        lbl_backup = tk.Label(config_win, text=self.tr("backup_automatico", "Backup automático")+":", bg=config_bg, fg="black" if not self.tema_oscuro else "white")
        lbl_backup.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        backup_selector = tk.Checkbutton(config_win, text=self.tr("backup_automatico", "Backup automático"), variable=backup_var, bg=config_bg, fg="black" if not self.tema_oscuro else "white", selectcolor=config_bg)
        backup_selector.grid(row=2, column=1, sticky="w", padx=10, pady=10)

        btn_borrar = ttk.Button(config_win, text=self.tr("Borrar_Cache", "Borrar Cache" if self.idioma == 'es' else "Clear Cache"), command=self.borrar_cache)
        btn_borrar.grid(row=3, column=0, columnspan=2, pady=10)
        btn_borrar_backups = ttk.Button(config_win, text=self.tr("Borrar_Backups", "Borrar Backups" if self.idioma == 'es' else "Delete Backups"), command=self.borrar_backups)
        btn_borrar_backups.grid(row=4, column=0, columnspan=2, pady=8)
        btn_cerrar = ttk.Button(config_win, text=self.tr("Cerrar", "Cerrar" if self.idioma == 'es' else "Close"), command=config_win.destroy)
        btn_cerrar.grid(row=5, column=0, columnspan=2, pady=10)

        def refrescar_ui_config():
            color_actual = coloresClaros['fondo'] if not self.tema_oscuro else coloresOscuros['fondo']
            color_texto = "black" if not self.tema_oscuro else "white"
            config_win.configure(bg=color_actual)
            config_win.title(self.tr("configuraciones", "Configuraciones"))

            lbl_idioma.config(text=self.tr("Idioma", "Idioma") + ":", bg=color_actual, fg=color_texto)
            lbl_tema.config(text=self.tr("Tema", "Tema") + ":", bg=color_actual, fg=color_texto)
            tema_selector.config(text=self.tr("Tema", "Tema"), bg=color_actual, fg=color_texto, selectcolor=color_actual)
            lbl_backup.config(text=self.tr("backup_automatico", "Backup automático") + ":", bg=color_actual, fg=color_texto)
            backup_selector.config(text=self.tr("backup_automatico", "Backup automático"), bg=color_actual, fg=color_texto, selectcolor=color_actual)
            btn_borrar.config(text=self.tr("Borrar_Cache", "Borrar Cache" if self.idioma == 'es' else "Clear Cache"))
            btn_borrar_backups.config(text=self.tr("Borrar_Backups", "Borrar Backups" if self.idioma == 'es' else "Delete Backups"))
            btn_cerrar.config(text=self.tr("Cerrar", "Cerrar" if self.idioma == 'es' else "Close"))

            estado["actualizando_idioma"] = True
            opciones = list(idioma_codigo_a_nombre().values())
            menu = om_idioma["menu"]
            menu.delete(0, "end")
            for opcion in opciones:
                menu.add_command(label=opcion, command=lambda valor=opcion: idioma_var.set(valor))
            idioma_var.set(idioma_codigo_a_nombre().get(self.idioma, self.idioma))
            estado["actualizando_idioma"] = False

        def actualizar_idioma(*args):
            if estado["actualizando_idioma"]:
                return
            seleccionado = idioma_nombre_a_codigo(idioma_var.get())
            if seleccionado != self.idioma:
                self.cambiar_idioma_manual(seleccionado)
            refrescar_ui_config()
        idioma_var.trace("w", actualizar_idioma)

        def actualizar_tema(*args):
            self.tema_oscuro = tema_var.get()
            self.aplicar_tema()
            self.guardar_preferencia_tema()
            refrescar_ui_config()
        tema_var.trace("w", actualizar_tema)

        def actualizar_backup(*args):
            self.backup_habilitado = backup_var.get()
            guardar_preferencia_backup(self.backup_habilitado)
        backup_var.trace("w", actualizar_backup)

        refrescar_ui_config()

    def aplicar_tema(self):
        # Aplica el tema usando la función de configs.py
        Config.aplicar_tema(self, oscuro=self.tema_oscuro)
        self.palette = self._palette()
        self._configurar_estilos_ttk()
        p = self.palette
        # Actualiza colores de frames y widgets
        color_fondo = p["panel"]
        color_fg = p["text"]
        # Frames
        self.main_frame.config(bg=color_fondo)
        self.top_frame.config(bg=color_fondo)
        self.texto_seleccionable.config(bg=p["surface"], fg=color_fg, highlightbackground=p["border"], insertbackground=color_fg)
        self.cuadro_traduccion.config(bg=p["surface"], fg=color_fg, highlightbackground=p["border"], insertbackground=color_fg)
        self.nav_frame.config(bg=color_fondo)
        self.botones_frame.config(bg=color_fondo)
        self.nav_buttons_row.config(bg=color_fondo)
        self.progress_frame.config(bg=color_fondo)
        self.etiqueta_archivo.config(bg=color_fondo, fg=color_fg)
        self.etiqueta_progreso.config(bg=color_fondo, fg=color_fg)
        if hasattr(self, "lbl_origen"):
            self.lbl_origen.config(bg=color_fondo, fg=p["muted"])
        if hasattr(self, "lbl_trad"):
            self.lbl_trad.config(bg=color_fondo, fg=p["muted"])
        for w in self.winfo_children():
            if isinstance(w, tk.Toplevel):
                w.config(bg=color_fondo)


    def cambiar_idioma_manual(self, nuevo_idioma):
        self.idioma = nuevo_idioma
        guardar_preferencia_idioma(self.idioma)
        # Actualizar todos los textos de la UI
        self.boton_buscar.config(text="🔍 " + self.tr("buscar_archivo", "Buscar archivo"))
        self.boton_copiar.config(text="📋 " + self.tr("copiar", "Copiar"))
        self.boton_guardar.config(text="💾 " + self.tr("guardar", "Guardar"))
        self.boton_anterior.config(text="← " + self.tr("anterior", "Anterior"))
        self.boton_siguiente.config(text=self.tr("siguiente", "Siguiente") + " →")
        self.boton_ir_vacias.config(text="🕳 " + self.tr("ir_a_vacias", "Ir a vacías"))
        self.boton_configuraciones.config(text="⚙ " + self.tr("configuraciones", "Configuraciones"))
        self.boton_recargar.config(text="⟳ " + self.tr("Recargar", "Recargar"))
        self.boton_backups.config(text="🗂 " + self.tr("Backups", "Backups"))
        self.boton_lista_lineas.config(text="📄 " + self.tr("Ver_Lineas", "Ver líneas"))
        self.boton_autorellenar.config(text="✨ " + self.tr("Auto_Rellenar", "Auto Rellenar"))
        self.check_autoguardar_nav.config(text="✓ " + self.tr("auto_guardar_nav", "Auto-guardar al navegar"))
        self.check_guardar_duplicadas.config(text="✓ " + self.tr("guardar_en_duplicadas", "Guardar en duplicadas"))
        self.lbl_origen.config(text=self.tr("Dialogo", "Diálogo"))
        self.lbl_trad.config(text=self.tr("Traduccion", "Traducción"))
        archivo_text = os.path.basename(self.ruta_archivo) if self.ruta_archivo else self.tr("ningun_archivo", "Ningún archivo seleccionado")
        self.etiqueta_archivo.config(text=f"{self.tr('archivo_seleccionado', 'Archivo seleccionado:')} {archivo_text}")
        self.buscador.delete(0, tk.END)
        self.buscador.insert(0, self.tr("buscar_linea", "Buscar línea"))

        if not self.ruta_archivo:
            self.texto_seleccionable.config(state=tk.NORMAL)
            self.texto_seleccionable.delete("1.0", tk.END)
            self.texto_seleccionable.insert("1.0", self.tr("placeholder_texto_original", "[Texto original]"))
            self.texto_seleccionable.config(state=tk.DISABLED)

            self.cuadro_traduccion.delete("1.0", tk.END)
            self.cuadro_traduccion.insert("1.0", self.tr("placeholder_traduccion", "[Traducción]"))

    def _es_linea_dialogo(self, linea):
        linea = linea.strip()
        return (linea.startswith('#') and linea.count('"') >= 2) or linea.startswith('old "')

    def _extraer_texto_entre_comillas(self, texto):
        indices = [i for i, c in enumerate(texto) if c == '"']
        if len(indices) >= 2:
            return texto[indices[0] + 1:indices[-1]]
        return texto.strip()

    def _cache_dialogos_path(self, archivo):
        return os.path.join(self.cache_dir, f"cache-dialogos-{os.path.basename(archivo)}.json")

    def _detectar_grupos_repetidos(self):
        grupos = {}
        for idx, linea in enumerate(self.lineas):
            if not self._es_linea_dialogo(linea):
                continue

            if idx >= len(self.lineas):
                continue

            dialogo = self._extraer_texto_entre_comillas(self.lineas[idx].strip()).strip()
            if not dialogo:
                continue

            if dialogo not in grupos:
                grupos[dialogo] = {
                    "dialogo": dialogo,
                    "lineas_idx": [],
                    "traducciones": [],
                }

            grupos[dialogo]["lineas_idx"].append(idx)

            traduccion = ""
            if idx + 1 < len(self.lineas):
                traduccion = self._extraer_texto_entre_comillas(self.lineas[idx + 1].strip()).strip()
            if traduccion and traduccion not in grupos[dialogo]["traducciones"]:
                grupos[dialogo]["traducciones"].append(traduccion)

        repetidos = []
        for grupo in grupos.values():
            if len(grupo["lineas_idx"]) <= 1:
                continue

            vacias = 0
            for idx in grupo["lineas_idx"]:
                trad = ""
                if idx + 1 < len(self.lineas):
                    trad = self._extraer_texto_entre_comillas(self.lineas[idx + 1].strip()).strip()
                if not trad:
                    vacias += 1

            traducciones_unicas = len(grupo["traducciones"])

            necesita_accion = vacias > 0 or traducciones_unicas > 1
            if necesita_accion:
                repetidos.append(grupo)

        repetidos.sort(key=lambda g: g["lineas_idx"][0])
        return repetidos

    def _obtener_indices_mismo_dialogo(self, idx_comentario):
        if not (0 <= idx_comentario < len(self.lineas)):
            return [idx_comentario]

        dialogo_base = self._extraer_texto_entre_comillas(self.lineas[idx_comentario].strip()).strip()
        if not dialogo_base:
            return [idx_comentario]

        indices = []
        for idx, linea in enumerate(self.lineas):
            if not self._es_linea_dialogo(linea):
                continue
            dialogo = self._extraer_texto_entre_comillas(linea.strip()).strip()
            if dialogo == dialogo_base:
                indices.append(idx)

        return indices if indices else [idx_comentario]

    def _aplicar_traduccion_en_linea(self, idx_comentario, traduccion):
        idx_traduccion = idx_comentario + 1
        if idx_traduccion >= len(self.lineas):
            return False

        linea = self.lineas[idx_traduccion]
        comillas_abiertas = linea.find('"')
        comillas_cerradas = linea.rfind('"')

        if comillas_abiertas == -1 or comillas_cerradas == -1 or comillas_abiertas >= comillas_cerradas:
            return False

        self.lineas[idx_traduccion] = f"{linea[:comillas_abiertas + 1]}{traduccion}{linea[comillas_cerradas:]}"
        return True

    def _guardar_lineas_en_archivo(self):
        if not self.ruta_archivo:
            raise OSError(self.tr("archivo_no_cargado", "No se ha cargado un archivo."))

        ruta_tmp = self.ruta_archivo + ".tmp"
        with io.open(ruta_tmp, "w", newline="", encoding="utf-8") as f:
            f.writelines(self.lineas)
        os.replace(ruta_tmp, self.ruta_archivo)

    def _crear_backup_previo(self, ruta_origen=None):
        ruta_base = ruta_origen if ruta_origen else self.ruta_archivo

        if not ruta_base:
            return
        if not os.path.isfile(ruta_base):
            return

        nombre_archivo = os.path.basename(ruta_base)
        nombre_base, extension = os.path.splitext(nombre_archivo)
        carpeta_archivo = os.path.join(self.backups_root_dir, nombre_base)
        os.makedirs(carpeta_archivo, exist_ok=True)

        marca_tiempo = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        extension_final = extension if extension else ".bak"
        nombre_backup = f"{nombre_base}-{marca_tiempo}{extension_final}"
        ruta_backup = os.path.join(carpeta_archivo, nombre_backup)

        shutil.copy2(ruta_base, ruta_backup)

        limite_backups = 3
        backups_archivo = []
        for nombre in os.listdir(carpeta_archivo):
            ruta = os.path.join(carpeta_archivo, nombre)
            if os.path.isfile(ruta):
                backups_archivo.append(ruta)

        if len(backups_archivo) > limite_backups:
            backups_archivo.sort(key=lambda ruta: os.path.getmtime(ruta), reverse=True)
            for ruta_vieja in backups_archivo[limite_backups:]:
                try:
                    os.remove(ruta_vieja)
                except Exception:
                    pass

    def _obtener_carpeta_backups_archivo(self, ruta_archivo=None):
        ruta = ruta_archivo if ruta_archivo else self.ruta_archivo
        if not ruta:
            return None
        nombre_archivo = os.path.basename(ruta)
        nombre_base, _ext = os.path.splitext(nombre_archivo)
        return os.path.join(self.backups_root_dir, nombre_base)

    def abrir_ventana_backups(self):
        if not self.ruta_archivo:
            messagebox.showwarning(self.tr("advertencia", "Advertencia"), self.tr("sin_archivo_para_backups", "No hay archivo cargado para gestionar backups."))
            return

        p = self.palette
        win = tk.Toplevel(self)
        win.title(self.tr("ventana_backups", "Backups del archivo"))
        win.geometry("860x500")
        win.config(bg=p["panel"])

        titulo = tk.Label(
            win,
            text=f"{self.tr('ventana_backups', 'Backups del archivo')}: {os.path.basename(self.ruta_archivo)}",
            bg=p["panel"],
            fg=p["text"],
            font=("Segoe UI", 12, "bold"),
        )
        titulo.pack(anchor="w", padx=12, pady=(12, 8))

        frame_tree = tk.Frame(win, bg=p["panel"], padx=12, pady=6)
        frame_tree.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame_tree, columns=("Nombre", "Fecha", "Tamano"), show="headings")
        tree.heading("Nombre", text=self.tr("nombre", "Nombre"))
        tree.heading("Fecha", text=self.tr("fecha", "Fecha"))
        tree.heading("Tamano", text=self.tr("tamano", "Tamaño"))
        tree.column("Nombre", width=450, anchor="w")
        tree.column("Fecha", width=220, anchor="center")
        tree.column("Tamano", width=120, anchor="center")

        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        estado = tk.Label(win, text="", bg=p["panel"], fg=p["muted"], font=("Segoe UI", 9, "bold"))
        estado.pack(anchor="w", padx=12, pady=(0, 8))

        backups_por_iid = {}

        def cargar_backups():
            tree.delete(*tree.get_children())
            backups_por_iid.clear()

            carpeta = self._obtener_carpeta_backups_archivo(self.ruta_archivo)
            archivos = []
            if carpeta and os.path.isdir(carpeta):
                for nombre in os.listdir(carpeta):
                    ruta = os.path.join(carpeta, nombre)
                    if os.path.isfile(ruta):
                        archivos.append(ruta)

            archivos.sort(key=lambda ruta: os.path.getmtime(ruta), reverse=True)

            if not archivos:
                estado.config(text=self.tr("sin_backups_disponibles", "No hay backups disponibles para este archivo."))
                return

            for idx, ruta in enumerate(archivos):
                nombre = os.path.basename(ruta)
                fecha = datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%Y-%m-%d %H:%M:%S")
                tamano_kb = max(1, int((os.path.getsize(ruta) + 1023) / 1024))
                iid = f"b{idx}"
                backups_por_iid[iid] = ruta
                tree.insert("", "end", iid=iid, values=(nombre, fecha, f"{tamano_kb} KB"))

            estado.config(text=f"{self.tr('total', 'Total')}: {len(archivos)}")

        def restaurar_seleccionado():
            sel = tree.focus().strip()
            if not sel or sel not in backups_por_iid:
                messagebox.showwarning(self.tr("advertencia", "Advertencia"), self.tr("selecciona_backup", "Selecciona un backup."))
                return

            ruta_backup = backups_por_iid[sel]
            confirmar = messagebox.askyesno(
                self.tr("restaurar_backup", "Restaurar backup"),
                self.tr("confirmar_restaurar_backup", "¿Restaurar este backup y reemplazar el archivo cargado actual?"),
            )
            if not confirmar:
                return

            try:
                shutil.copy2(ruta_backup, self.ruta_archivo)
                self.cargar_archivo_en_cache(self.ruta_archivo, crear_backup_apertura=False)
                estado.config(text=self.tr("backup_restaurado", "Backup restaurado correctamente."))
            except Exception as e:
                messagebox.showerror(self.tr("error", "Error"), self.tr("error_restaurar_backup", "No se pudo restaurar el backup: ") + str(e))

        acciones = tk.Frame(win, bg=p["panel"], padx=12, pady=10)
        acciones.pack(fill=tk.X)

        btn_restaurar = ttk.Button(
            acciones,
            text="↺ " + self.tr("restaurar_backup", "Restaurar backup"),
            style="Primary.TButton",
            command=restaurar_seleccionado,
        )
        btn_restaurar.pack(side=tk.LEFT)

        btn_actualizar = ttk.Button(
            acciones,
            text="⟳ " + self.tr("Recargar", "Recargar"),
            style="Ghost.TButton",
            command=cargar_backups,
        )
        btn_actualizar.pack(side=tk.LEFT, padx=8)

        btn_cerrar = ttk.Button(
            acciones,
            text=self.tr("Cerrar", "Cerrar"),
            style="Ghost.TButton",
            command=win.destroy,
        )
        btn_cerrar.pack(side=tk.RIGHT)

        cargar_backups()

    def _registrar_cambio_historial(self, cambios, origen="manual"):
        cambios_filtrados = []
        for idx_trad, anterior, nuevo in cambios:
            if anterior != nuevo:
                cambios_filtrados.append((idx_trad, anterior, nuevo))

        if not cambios_filtrados:
            return

        self._historial_seq += 1
        self.historial_cambios.append({
            "id": self._historial_seq,
            "origen": origen,
            "cambios": cambios_filtrados,
        })

        if len(self.historial_cambios) > self.max_historial_cambios:
            exceso = len(self.historial_cambios) - self.max_historial_cambios
            del self.historial_cambios[:exceso]

        self.actualizar_botones()

    def _deshacer_evento_historial(self, evento, mostrar_feedback=True):
        restauracion_reversa = []

        for idx_trad, anterior, _nuevo in evento["cambios"]:
            if 0 <= idx_trad < len(self.lineas):
                restauracion_reversa.append((idx_trad, self.lineas[idx_trad]))
                self.lineas[idx_trad] = anterior

        try:
            self._guardar_lineas_en_archivo()
        except Exception as e:
            for idx_trad, valor_actual in restauracion_reversa:
                if 0 <= idx_trad < len(self.lineas):
                    self.lineas[idx_trad] = valor_actual
            messagebox.showerror(self.tr("error", "Error"), self.tr("error_deshacer", "No se pudo deshacer: ") + str(e))
            return False

        if self.indices_comentarios:
            self.cargar_linea(self.indice_linea)
            self.actualizar_progreso()

        if mostrar_feedback:
            cantidad = len(evento["cambios"])
            self.etiqueta_progreso.config(text=f"{self.tr('deshecho', 'Deshecho')}: {cantidad}")
            self.after(900, self.actualizar_progreso)

        return True

    def _lineas_evento_historial(self, evento):
        lineas = sorted({idx + 1 for idx, _anterior, _nuevo in evento.get("cambios", [])})
        return ", ".join(str(x) for x in lineas[:6]) + ("..." if len(lineas) > 6 else "")

    def abrir_historial_deshacer(self, parent=None, on_change=None):
        if not self.historial_cambios:
            messagebox.showinfo(self.tr("info", "Info"), self.tr("sin_historial", "No hay cambios para deshacer."))
            return

        p = self.palette
        top = tk.Toplevel(parent if parent is not None else self)
        top.title(self.tr("historial_cambios", "Historial de cambios"))
        top.geometry("760x420")
        top.config(bg=p["panel"])

        header = tk.Label(
            top,
            text=self.tr("elige_deshacer", "Selecciona una acción y deshaz hasta ese punto:"),
            bg=p["panel"],
            fg=p["text"],
            font=("Segoe UI", 11, "bold"),
        )
        header.pack(anchor="w", padx=12, pady=(12, 8))

        frame_tree = tk.Frame(top, bg=p["panel"], padx=12, pady=4)
        frame_tree.pack(fill=tk.BOTH, expand=True)

        cols = ("Id", "Accion", "Cambios", "Lineas")
        tree = ttk.Treeview(frame_tree, columns=cols, show="headings")
        tree.heading("Id", text="#")
        tree.heading("Accion", text=self.tr("accion", "Acción"))
        tree.heading("Cambios", text=self.tr("cambios", "Cambios"))
        tree.heading("Lineas", text=self.tr("Lineas", "Líneas"))
        tree.column("Id", width=70, anchor="center")
        tree.column("Accion", width=130, anchor="center")
        tree.column("Cambios", width=100, anchor="center")
        tree.column("Lineas", width=380, anchor="w")

        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        estado_lbl = tk.Label(top, text="", bg=p["panel"], fg=p["muted"], font=("Segoe UI", 9, "bold"))
        estado_lbl.pack(anchor="w", padx=12, pady=(2, 4))

        def poblar():
            tree.delete(*tree.get_children())
            for idx in range(len(self.historial_cambios) - 1, -1, -1):
                evento = self.historial_cambios[idx]
                origen = evento.get("origen", "manual")
                accion_txt = self.tr("accion_auto", "Auto") if origen == "auto" else self.tr("accion_manual", "Manual")
                cantidad = len(evento.get("cambios", []))
                lineas_txt = self._lineas_evento_historial(evento)
                tree.insert("", "end", iid=str(idx), values=(evento.get("id", idx + 1), accion_txt, cantidad, lineas_txt))
            estado_lbl.config(text=f"{self.tr('total', 'Total')}: {len(self.historial_cambios)}")

        def deshacer_seleccionado():
            sel = tree.focus().strip()
            if not sel:
                messagebox.showwarning(self.tr("advertencia", "Advertencia"), self.tr("selecciona_historial", "Selecciona un elemento del historial."))
                return

            try:
                idx_objetivo = int(sel)
            except ValueError:
                return

            cantidad_deshacer = len(self.historial_cambios) - idx_objetivo
            if cantidad_deshacer <= 0:
                return

            hechos = 0
            while len(self.historial_cambios) > idx_objetivo:
                evento = self.historial_cambios.pop()
                ok = self._deshacer_evento_historial(evento, mostrar_feedback=False)
                if not ok:
                    self.historial_cambios.append(evento)
                    break
                hechos += 1

            self.actualizar_botones()
            poblar()

            if on_change:
                on_change()

            if hechos > 0:
                estado_lbl.config(text=f"{self.tr('deshecho', 'Deshecho')}: {hechos}")
            if not self.historial_cambios:
                estado_lbl.config(text=self.tr("sin_historial", "No hay cambios para deshacer."))

        acciones = tk.Frame(top, bg=p["panel"], padx=12, pady=10)
        acciones.pack(fill=tk.X)

        btn_deshacer_sel = ttk.Button(
            acciones,
            text="↶ " + self.tr("deshacer_seleccion", "Deshacer selección"),
            style="Secondary.TButton",
            command=deshacer_seleccionado,
        )
        btn_deshacer_sel.pack(side=tk.LEFT)

        btn_cerrar = ttk.Button(
            acciones,
            text=self.tr("Cerrar", "Cerrar"),
            style="Ghost.TButton",
            command=top.destroy,
        )
        btn_cerrar.pack(side=tk.RIGHT)

        poblar()

    def cargar_archivo_en_cache(self, archivo, crear_backup_apertura=False):
        self._carga_token += 1
        token = self._carga_token
        self.etiqueta_archivo.config(text=self.tr("cargando_archivo", "Cargando archivo..."))

        def load_file():
            try:
                with io.open(archivo, 'r', newline='', encoding='utf-8') as f:
                    lineas = f.readlines()

                cache_path = self._cache_dialogos_path(archivo)
                dialogos_json = None
                all_indices_comentarios = []

                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, "r", encoding="utf-8") as fjson:
                            cache_data = json.load(fjson)
                        if isinstance(cache_data, dict):
                            dialogos_json = cache_data
                            for valor in cache_data.values():
                                if isinstance(valor, dict):
                                    lineas_cache = valor.get("lineas")
                                    if isinstance(lineas_cache, list) and lineas_cache:
                                        idx = lineas_cache[0]
                                        if isinstance(idx, int) and 0 <= idx < len(lineas):
                                            all_indices_comentarios.append(idx)
                    except Exception:
                        dialogos_json = None
                        all_indices_comentarios = []

                if not all_indices_comentarios:
                    all_indices_comentarios = [i for i, linea in enumerate(lineas) if self._es_linea_dialogo(linea)]
                    dialogos_json = None

                self.after(0, lambda: self._finalizar_carga(token, archivo, lineas, all_indices_comentarios, dialogos_json, crear_backup_apertura))
            except Exception as e:
                self.after(0, lambda: self._error_carga(token, e))

        threading.Thread(target=load_file, daemon=True).start()

    def _error_carga(self, token, error):
        if token != self._carga_token:
            return
        self.etiqueta_archivo.config(text=self.tr("ningun_archivo", "Ningún archivo seleccionado"))
        messagebox.showerror(self.tr("error", "Error"), f"{self.tr('error_lectura', 'No se pudo leer el archivo: ')}{error}")

    def _finalizar_carga(self, token, archivo, lineas, all_indices_comentarios, dialogos_json, crear_backup_apertura=False):
        if token != self._carga_token:
            return

        if crear_backup_apertura and self.backup_habilitado:
            try:
                self._crear_backup_previo(archivo)
            except Exception as e:
                messagebox.showwarning(
                    self.tr("advertencia", "Advertencia"),
                    self.tr("error_backup_guardado", "No se pudo crear backup, pero el archivo se guardó: ") + str(e),
                )

        self.ruta_archivo = archivo
        self.lineas = lineas
        self.historial_cambios = []
        self.dialogos_json = dialogos_json
        self.all_indices_comentarios = all_indices_comentarios
        self.indices_comentarios = list(all_indices_comentarios)
        self.total_lineas = len(self.indices_comentarios)
        self.indice_linea = 0

        nombre = os.path.basename(archivo)
        self.etiqueta_archivo.config(text=f"{self.tr('archivo_seleccionado', 'Archivo seleccionado:')} {nombre}")

        if self.indices_comentarios:
            self.cargar_linea(0)
        else:
            self.actualizar_texto_traducir("", "")
            messagebox.showinfo(self.tr("info", "Info"), self.tr("no_comentarios", "No se encontraron comentarios"))

        self.actualizar_progreso()
        self.actualizar_botones()

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title=self.tr("buscar_archivo", "Buscar archivo"),
            filetypes=[("Archivos Ren'Py", "*.rpy"), ("Todos", "*.*")]
        )
        if not archivo:
            return
        self.cargar_archivo_en_cache(archivo, crear_backup_apertura=True)

    def recargar_archivo(self):
        if not self.ruta_archivo:
            messagebox.showwarning(self.tr("error", "Error"), self.tr("archivo_no_cargado", "No se ha cargado un archivo."))
            return
        self.cargar_archivo_en_cache(self.ruta_archivo, crear_backup_apertura=False)

    def ir_a_linea_vacia(self):
        if not self.indices_comentarios:
            messagebox.showinfo(self.tr("info", "Info"), self.tr("archivo_no_cargado", "No se ha cargado un archivo."))
            return

        lineas_vacias = self._obtener_posiciones_vacias()
        if lineas_vacias:
            self.cargar_linea(lineas_vacias[0])
            self.actualizar_botones()
            return

        messagebox.showinfo(self.tr("info", "Info"), self.tr("sin_lineas_vacias", "No se encontraron líneas vacías."))

    def _obtener_posiciones_vacias(self):
        posiciones = []
        for pos, idx in enumerate(self.indices_comentarios):
            if idx + 1 >= len(self.lineas):
                continue
            traduccion = self._extraer_texto_entre_comillas(self.lineas[idx + 1].strip())
            if not traduccion:
                posiciones.append(pos)
        return posiciones

    def actualizar_progreso(self):
        actual = self.indice_linea + 1 if self.total_lineas > 0 else 0
        self.etiqueta_progreso.config(text=f"{actual}/{self.total_lineas}")

    def cargar_linea(self, indice):
        if not (0 <= indice < len(self.indices_comentarios)):
            return
        self.indice_linea = indice
        idx = self.indices_comentarios[indice]
        linea_origen = self.lineas[idx].strip() if idx < len(self.lineas) else ""
        origen = self._extraer_texto_entre_comillas(linea_origen)
        traduccion = ""
        if idx + 1 < len(self.lineas):
            traduccion = self._extraer_texto_entre_comillas(self.lineas[idx + 1].strip())

        self.texto_seleccionable.config(state=tk.NORMAL)
        self.texto_seleccionable.delete("1.0", tk.END)
        self.texto_seleccionable.insert(tk.END, f"{idx + 1}: {origen}")
        self.texto_seleccionable.config(state=tk.DISABLED)
        self.cuadro_traduccion.delete("1.0", tk.END)
        self.cuadro_traduccion.insert(tk.END, traduccion)
        self.actualizar_progreso()

    def actualizar_texto_traducir(self, texto, traduccion):
        self.texto_seleccionable.config(state=tk.NORMAL)
        self.texto_seleccionable.delete("1.0", tk.END)
        self.texto_seleccionable.insert(tk.END, texto)
        self.texto_seleccionable.config(state=tk.DISABLED)
        self.cuadro_traduccion.delete("1.0", tk.END)
        self.cuadro_traduccion.insert(tk.END, traduccion)

    def copiar_texto(self):
        texto = self.texto_seleccionable.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo(self.tr("copiado", "Copiado"), self.tr("texto_copiado", "Texto copiado al portapapeles."))

    def guardar_traduccion(self, mostrar_feedback=True):
        if not self.ruta_archivo or not self.indices_comentarios:
            messagebox.showerror(self.tr("error", "Error"), self.tr("error_no_archivo", "No hay archivo cargado para guardar."))
            return False

        idx_comentario = self.indices_comentarios[self.indice_linea]
        traduccion = self.cuadro_traduccion.get("1.0", tk.END).strip()

        indices_objetivo = [idx_comentario]
        if self.guardar_duplicadas_var.get():
            indices_objetivo = self._obtener_indices_mismo_dialogo(idx_comentario)

        respaldo = {}
        cambios_historial = []
        cambios = 0
        lineas_validas = 0

        for idx_objetivo in indices_objetivo:
            idx_traduccion = idx_objetivo + 1
            if idx_traduccion >= len(self.lineas):
                continue

            linea_original = self.lineas[idx_traduccion]
            if not self._aplicar_traduccion_en_linea(idx_objetivo, traduccion):
                continue

            lineas_validas += 1

            linea_nueva = self.lineas[idx_traduccion]
            if linea_nueva != linea_original:
                respaldo[idx_traduccion] = linea_original
                cambios_historial.append((idx_traduccion, linea_original, linea_nueva))
                cambios += 1

        if lineas_validas == 0:
            messagebox.showerror(self.tr("error", "Error"), self.tr("error_guardar", "No se pudo guardar la traducción: ") + "línea de traducción inválida")
            return False

        if cambios == 0:
            if mostrar_feedback:
                messagebox.showinfo(self.tr("info", "Info"), self.tr("sin_cambios", "No hay cambios para guardar."))
            return True

        try:
            self._guardar_lineas_en_archivo()
        except Exception as e:
            for idx_traduccion, linea_original in respaldo.items():
                if idx_traduccion < len(self.lineas):
                    self.lineas[idx_traduccion] = linea_original
            messagebox.showerror(self.tr("error", "Error"), self.tr("error_guardar", "No se pudo guardar la traducción: ") + str(e))
            return False

        self._registrar_cambio_historial(cambios_historial, origen="manual")

        self.cargar_linea(self.indice_linea)
        self.actualizar_progreso()
        self.actualizar_botones()
        if mostrar_feedback:
            self.etiqueta_progreso.config(text=f"{self.indice_linea + 1}/{self.total_lineas} ✔")
            self.after(900, self.actualizar_progreso)
        return True

    def linea_anterior(self):
        if not self.indices_comentarios:
            return

        if self.auto_guardar_nav_var.get():
            guardado_ok = self.guardar_traduccion(mostrar_feedback=False)
            if not guardado_ok:
                return

        if self.indice_linea > 0:
            self.cargar_linea(self.indice_linea - 1)
        self.actualizar_botones()

    def linea_siguiente(self):
        if not self.indices_comentarios:
            return

        if self.auto_guardar_nav_var.get():
            guardado_ok = self.guardar_traduccion(mostrar_feedback=False)
            if not guardado_ok:
                return

        if self.indice_linea < len(self.indices_comentarios) - 1:
            self.cargar_linea(self.indice_linea + 1)
        self.actualizar_botones()

    def actualizar_botones(self):
        if not self.indices_comentarios:
            self.boton_anterior.config(state=tk.DISABLED)
            self.boton_siguiente.config(state=tk.DISABLED)
            self.boton_guardar.config(state=tk.DISABLED)
            return

        self.boton_anterior.config(state=tk.NORMAL if self.indice_linea > 0 else tk.DISABLED)
        self.boton_siguiente.config(state=tk.NORMAL if self.indice_linea < len(self.indices_comentarios) - 1 else tk.DISABLED)
        self.boton_guardar.config(state=tk.NORMAL)

    def buscar_por_linea(self):
        if not self.indices_comentarios:
            messagebox.showinfo(self.tr("info", "Info"), self.tr("archivo_no_cargado", "No se ha cargado un archivo."))
            return

        valor = self.buscador.get().strip()
        try:
            linea_buscada = int(valor) - 1
        except ValueError:
            messagebox.showerror(self.tr("error", "Error"), self.tr("buscar_linea", "Buscar línea") + ": número inválido")
            return

        if linea_buscada in self.indices_comentarios:
            posicion = self.indices_comentarios.index(linea_buscada)
            self.cargar_linea(posicion)
            self.actualizar_botones()
            return

        messagebox.showinfo(self.tr("info", "Info"), self.tr("no_comentarios", "No se encontraron comentarios"))

    def actualizar_boton_autorellenar(self):
        self.boton_autorellenar.config(state=tk.NORMAL)

    def auto_rellenar_traducciones(self):
        if not self.ruta_archivo or not self.indices_comentarios:
            messagebox.showwarning(self.tr("error", "Error"), self.tr("archivo_no_cargado", "No se ha cargado un archivo."))
            return

        grupos = self._detectar_grupos_repetidos()
        if not grupos:
            messagebox.showinfo(
                self.tr("info", "Info"),
                self.tr("sin_repetidos", "No se encontraron diálogos repetidos para aplicar automáticamente."),
            )
            return

        p = self.palette
        win = tk.Toplevel(self)
        win.title(self.tr("gestion_repetidos", "Gestión de diálogos repetidos"))
        win.geometry("900x600")
        win.config(bg=p["panel"])

        tree = ttk.Treeview(win, columns=("Dialogo", "Lineas", "Traducciones"), show="headings")
        tree.heading("Dialogo", text=self.tr("Dialogo", "Diálogo"))
        tree.heading("Lineas", text=self.tr("Lineas", "Líneas"))
        tree.heading("Traducciones", text=self.tr("Traducciones", "Traducciones"))
        tree.column("Dialogo", width=350)
        tree.column("Lineas", width=120)
        tree.column("Traducciones", width=300)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        grupos_por_iid = {}
        for n, grupo in enumerate(grupos):
            iid = f"g{n}"
            grupos_por_iid[iid] = grupo
            lineas_txt = ", ".join(str(i + 1) for i in grupo["lineas_idx"])
            traducciones_txt = " | ".join(grupo["traducciones"]) if grupo["traducciones"] else self.tr("sin_traducciones", "(sin traducciones)")
            tree.insert("", "end", iid=iid, values=(grupo["dialogo"], lineas_txt, traducciones_txt))

        frame_edicion = tk.Frame(win, bg=p["panel"])
        frame_edicion.pack(fill=tk.X, padx=10, pady=10)

        lbl = tk.Label(
            frame_edicion,
            text=self.tr("selecciona_dialogo_editar", "Selecciona un diálogo para editar sus traducciones:"),
            bg=p["panel"],
            fg=p["text"],
            font=("Segoe UI", 11),
        )
        lbl.pack(anchor="w")

        txt_dialogo = tk.Text(frame_edicion, height=2, font=("Segoe UI", 11), state=tk.DISABLED)
        txt_dialogo.pack(fill=tk.X, pady=4)

        from tkinter import StringVar

        trad_var = StringVar()
        combo_trads = ttk.Combobox(frame_edicion, textvariable=trad_var, font=("Segoe UI", 11), state="readonly")
        combo_trads.pack(fill=tk.X, pady=4)

        lbl_perso = tk.Label(
            frame_edicion,
            text=self.tr("traduccion_personalizada", "O escribe una traducción personalizada:"),
            bg=p["panel"],
            fg=p["text"],
            font=("Segoe UI", 10),
        )
        lbl_perso.pack(anchor="w", pady=(8, 0))
        entry_perso = tk.Entry(frame_edicion, font=("Segoe UI", 11))
        entry_perso.pack(fill=tk.X, pady=(0, 6))

        lbl_lineas = tk.Label(
            frame_edicion,
            text="",
            bg=p["panel"],
            fg=p["muted"],
            font=("Segoe UI", 9),
        )
        lbl_lineas.pack(anchor="w", pady=(0, 8))

        lbl_estado = tk.Label(
            frame_edicion,
            text="",
            bg=p["panel"],
            fg=p["text"],
            font=("Segoe UI", 9, "bold"),
        )
        lbl_estado.pack(anchor="w", pady=(0, 8))

        acciones_auto = tk.Frame(frame_edicion, bg=p["panel"])
        acciones_auto.pack(fill=tk.X, pady=4)

        btn_historial = ttk.Button(
            acciones_auto,
            text="↶ " + self.tr("historial", "Historial"),
            style="Ghost.TButton",
            command=lambda: self.abrir_historial_deshacer(parent=win, on_change=refrescar_grupos),
        )
        btn_historial.pack(side=tk.LEFT)

        btn_aplicar = ttk.Button(
            acciones_auto,
            text=self.tr("aplicar_traduccion_todas", "Aplicar traducción a todas las líneas"),
            state=tk.DISABLED,
        )
        btn_aplicar.pack(side=tk.RIGHT)

        seleccion_actual = {"iid": None}

        def refrescar_grupos():
            nuevos_grupos = self._detectar_grupos_repetidos()

            tree.delete(*tree.get_children())
            grupos_por_iid.clear()

            for n, grupo in enumerate(nuevos_grupos):
                iid_nuevo = f"g{n}"
                grupos_por_iid[iid_nuevo] = grupo
                lineas_txt = ", ".join(str(i + 1) for i in grupo["lineas_idx"])
                traducciones_txt = " | ".join(grupo["traducciones"]) if grupo["traducciones"] else self.tr("sin_traducciones", "(sin traducciones)")
                tree.insert("", "end", iid=iid_nuevo, values=(grupo["dialogo"], lineas_txt, traducciones_txt))

            seleccion_actual["iid"] = None
            combo_trads.set("")
            combo_trads["values"] = []
            txt_dialogo.config(state=tk.NORMAL)
            txt_dialogo.delete("1.0", tk.END)
            txt_dialogo.config(state=tk.DISABLED)
            lbl_lineas.config(text="")
            entry_perso.delete(0, tk.END)
            btn_aplicar.config(state=tk.DISABLED)

            if grupos_por_iid:
                combo_trads.config(state="readonly")
                entry_perso.config(state="normal")
            else:
                combo_trads.config(state="disabled")
                entry_perso.config(state="disabled")
                lbl_estado.config(text=self.tr("sin_repetidos_restantes", "No quedan grupos repetidos pendientes."))

        def on_select(event):
            sel = tree.focus().strip()
            if not sel or sel not in grupos_por_iid:
                return

            grupo = grupos_por_iid[sel]
            seleccion_actual["iid"] = sel

            txt_dialogo.config(state=tk.NORMAL)
            txt_dialogo.delete("1.0", tk.END)
            txt_dialogo.insert(tk.END, grupo["dialogo"])
            txt_dialogo.config(state=tk.DISABLED)

            candidatos = grupo["traducciones"][:]
            combo_trads["values"] = candidatos
            trad_var.set(candidatos[0] if candidatos else "")
            lbl_estado.config(text="")

            lineas_txt = ", ".join(str(i + 1) for i in grupo["lineas_idx"])
            lbl_lineas.config(text=f"{self.tr('Lineas', 'Líneas')}: {lineas_txt}")

            entry_perso.delete(0, tk.END)
            btn_aplicar.config(state=tk.NORMAL)

        tree.bind("<<TreeviewSelect>>", on_select)

        def aplicar_traduccion():
            iid = seleccion_actual["iid"]
            if not iid or iid not in grupos_por_iid:
                messagebox.showwarning(self.tr("advertencia", "Advertencia"), self.tr("debes_seleccionar_dialogo", "Debes seleccionar un diálogo."))
                return

            traduccion_perso = entry_perso.get().strip()
            traduccion_seleccionada = trad_var.get().strip()
            traduccion_final = traduccion_perso if traduccion_perso else traduccion_seleccionada

            if not traduccion_final:
                messagebox.showwarning(self.tr("advertencia", "Advertencia"), self.tr("debes_elegir_traduccion", "Debes elegir o escribir una traducción."))
                return

            grupo = grupos_por_iid[iid]
            indices = grupo["lineas_idx"]
            respaldo = {}
            cambios_historial = []
            cambios = 0
            for idx_comentario in indices:
                idx_trad = idx_comentario + 1
                if idx_trad < len(self.lineas):
                    linea_anterior = self.lineas[idx_trad]
                    respaldo[idx_trad] = linea_anterior
                if self._aplicar_traduccion_en_linea(idx_comentario, traduccion_final):
                    cambios += 1
                    if idx_trad < len(self.lineas):
                        linea_nueva = self.lineas[idx_trad]
                        cambios_historial.append((idx_trad, linea_anterior, linea_nueva))

            if cambios == 0:
                messagebox.showerror(self.tr("error", "Error"), self.tr("error_guardar", "No se pudo guardar la traducción: ") + self.tr("lineas_invalidas", "líneas inválidas"))
                return

            try:
                self._guardar_lineas_en_archivo()
            except Exception as e:
                for idx_trad, linea_original in respaldo.items():
                    if idx_trad < len(self.lineas):
                        self.lineas[idx_trad] = linea_original
                messagebox.showerror(self.tr("error", "Error"), self.tr("error_guardar", "No se pudo guardar la traducción: ") + str(e))
                return

            self._registrar_cambio_historial(cambios_historial, origen="auto")

            if self.indices_comentarios:
                self.cargar_linea(self.indice_linea)
                self.actualizar_progreso()

            tree.delete(iid)
            del grupos_por_iid[iid]
            seleccion_actual["iid"] = None
            combo_trads.set("")
            combo_trads["values"] = []
            entry_perso.delete(0, tk.END)
            txt_dialogo.config(state=tk.NORMAL)
            txt_dialogo.delete("1.0", tk.END)
            txt_dialogo.config(state=tk.DISABLED)
            lbl_lineas.config(text="")
            btn_aplicar.config(state=tk.DISABLED)
            lbl_estado.config(text=f"{self.tr('aplicadas_en', 'Traducción aplicada en')} {cambios} {self.tr('lineas', 'líneas')}.")

            if not grupos_por_iid:
                combo_trads.config(state="disabled")
                entry_perso.config(state="disabled")
                lbl_estado.config(text=self.tr("sin_repetidos_restantes", "No quedan grupos repetidos pendientes."))

        btn_aplicar.config(command=aplicar_traduccion)

    # ---------- Ventana de listado de líneas con Treeview ----------
    def abrir_lista_lineas(self):
        if not self.indices_comentarios:
            messagebox.showinfo(self.tr("info", "Info"), self.tr("archivo_no_cargado", "No se ha cargado un archivo."))
            return

        top = tk.Toplevel(self)
        top.title(self.tr("Ver_Lineas", "Ver líneas"))
        top.geometry("1100x760")
        p = self.palette
        top.config(bg=p["panel"])

        header = tk.Frame(top, bg=p["panel"], padx=12, pady=10)
        header.pack(fill=tk.X)

        total = len(self.indices_comentarios)
        vacias = len(self._obtener_posiciones_vacias())
        completas = total - vacias

        titulo = tk.Label(
            header,
            text=self.tr("Ver_Lineas", "Ver líneas"),
            font=("Segoe UI", 14, "bold"),
            bg=p["panel"],
            fg=p["text"],
        )
        titulo.pack(side=tk.LEFT)

        resumen = tk.Label(
            header,
            text=f"{self.tr('total_lineas', 'Total')}: {total}    {self.tr('completas', 'Completas')}: {completas}    {self.tr('vacias', 'Vacías')}: {vacias}",
            font=("Segoe UI", 10),
            bg=p["panel"],
            fg=p["muted"],
        )
        resumen.pack(side=tk.RIGHT)

        legend = tk.Frame(top, bg=p["panel"], padx=12)
        legend.pack(fill=tk.X, pady=(0, 8))
        tk.Label(legend, text="●", fg="#fff3cd", bg=p["panel"], font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(legend, text=self.tr("vacias", "Vacías"), bg=p["panel"], fg=p["muted"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(4, 14))
        tk.Label(legend, text="●", fg="#eef4ff", bg=p["panel"], font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(legend, text=self.tr("completas", "Completas"), bg=p["panel"], fg=p["muted"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(4, 0))

        style = ttk.Style(top)
        style.configure("Lines.Treeview", rowheight=28, font=("Segoe UI", 10), background=p["surface"], fieldbackground=p["surface"], foreground=p["text"])
        style.configure("Lines.Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=(6, 6))
        style.map("Lines.Treeview", background=[("selected", p["accent_hover"])], foreground=[("selected", "#ffffff")])

        if self.tema_oscuro:
            color_vacia_bg = "#5a4a2a"
            color_completa_bg = "#2f3e5a"
            color_descartado_bg = "#5a3035"
            color_fila_fg = "#f2f2f2"
        else:
            color_vacia_bg = "#fff3cd"
            color_completa_bg = "#eef4ff"
            color_descartado_bg = "#f8d7da"
            color_fila_fg = "#1f2328"

        tree_frame = tk.Frame(top, bg=p["panel"], padx=12, pady=6)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        columns = ("Linea", "Dialogo", "Traduccion")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Lines.Treeview", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side=tk.RIGHT, fill="y")
        hsb.pack(side=tk.BOTTOM, fill="x")
        tree.pack(fill=tk.BOTH, expand=True)
        tree.heading("Linea", text=self.tr("Linea", "Línea"))
        tree.heading("Dialogo", text=self.tr("Dialogo", "Diálogo"))
        tree.heading("Traduccion", text=self.tr("Traduccion", "Traducción"))
        tree.column("Linea", width=80, anchor="center")
        tree.column("Dialogo", width=470, anchor="w")
        tree.column("Traduccion", width=430, anchor="w")
        for idx in self.indices_comentarios:
            linea_num = idx + 1
            dialogo = self._extraer_texto_entre_comillas(self.lineas[idx].strip()) if idx < len(self.lineas) else ""
            traduccion = ""
            if idx + 1 < len(self.lineas):
                traduccion = self._extraer_texto_entre_comillas(self.lineas[idx + 1].strip())
            estado = "+" if traduccion else "–"
            tree.insert("", "end", iid=str(idx), values=(linea_num, dialogo, f"{estado} {traduccion}" if traduccion else estado))
            if not traduccion:
                tree.item(str(idx), tags=("vacia",))
            else:
                tree.item(str(idx), tags=("completa",))

        tree.tag_configure("vacia", background=color_vacia_bg, foreground=color_fila_fg)
        tree.tag_configure("completa", background=color_completa_bg, foreground=color_fila_fg)
        tree.tag_configure("descartado", background=color_descartado_bg, foreground=color_fila_fg)
        
        # Función para detectar clic derecho en una línea (toggle descartado)
        def on_right_click(event):
            item = tree.identify_row(event.y)
            if item:
                tags = tree.item(item, "tags")
                if "descartado" in tags:
                    tree.item(item, tags=())
                else:
                    tree.item(item, tags=("descartado",))
        tree.bind("<Button-3>", on_right_click)
        
        # Función para doble clic izquierdo: cargar la línea en el editor.
        def on_double_click(event):
            item = tree.identify_row(event.y)
            if item:
                idx = int(item)
                if idx in self.indices_comentarios:
                    self.cargar_linea(self.indices_comentarios.index(idx))
                    self.actualizar_botones()
        tree.bind("<Double-1>", on_double_click)

if __name__ == '__main__':
    app = Dorouh()
    app.mainloop()
