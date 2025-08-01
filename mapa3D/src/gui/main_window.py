"""
Ventana principal de la aplicación
=================================

Este módulo implementa la ventana principal de la aplicación para
generar mapas 3D del Ecuador.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
import sys

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.dem_loader import DEMLoader
from data_processing.ecuador_filter import EcuadorFilter
from data_processing.political_segmentation import PoliticalSegmentation

logger = logging.getLogger(__name__)


class MainWindow:
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mapa 3D del Ecuador - Generador")
        self.root.geometry("1000x700")
        
        # Componentes del procesamiento
        self.dem_loader = DEMLoader()
        self.ecuador_filter = EcuadorFilter()
        self.political_segmentation = PoliticalSegmentation()
        
        # Variables de estado
        self.current_dem_data = None
        self.processed_data = None
        
        self._setup_ui()
        self._setup_logging()
        
        logger.info("Ventana principal inicializada")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Generador de Mapas 3D del Ecuador", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de carga de datos
        self._create_data_loading_frame(main_frame)
        
        # Frame de configuración
        self._create_configuration_frame(main_frame)
        
        # Frame de procesamiento
        self._create_processing_frame(main_frame)
        
        # Frame de registro
        self._create_log_frame(main_frame)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_data_loading_frame(self, parent):
        """Crea el frame para carga de datos."""
        data_frame = ttk.LabelFrame(parent, text="1. Carga de Datos DEM", padding="10")
        data_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        data_frame.columnconfigure(1, weight=1)
        
        # Selección de archivo
        ttk.Label(data_frame, text="Archivo DEM:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(data_frame, textvariable=self.file_path_var, state='readonly')
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(data_frame, text="Examinar...", 
                  command=self._browse_dem_file).grid(row=0, column=2)
        
        ttk.Button(data_frame, text="Cargar DEM", 
                  command=self._load_dem_file).grid(row=0, column=3, padx=(10, 0))
        
        # Información del archivo
        self.file_info_var = tk.StringVar()
        self.file_info_var.set("No hay archivo cargado")
        ttk.Label(data_frame, textvariable=self.file_info_var, 
                 foreground="blue").grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
    
    def _create_configuration_frame(self, parent):
        """Crea el frame de configuración."""
        config_frame = ttk.LabelFrame(parent, text="2. Configuración", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configuraciones en dos columnas
        left_frame = ttk.Frame(config_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        
        right_frame = ttk.Frame(config_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.N))
        
        # Configuraciones de la izquierda
        ttk.Label(left_frame, text="Región:").grid(row=0, column=0, sticky=tk.W)
        self.region_var = tk.StringVar(value="Ecuador Continental")
        region_combo = ttk.Combobox(left_frame, textvariable=self.region_var, 
                                   values=["Ecuador Continental", "Costa", "Sierra", "Oriente"])
        region_combo.grid(row=0, column=1, padx=(10, 0), pady=(0, 5))
        region_combo.state(['readonly'])
        
        ttk.Label(left_frame, text="Resolución:").grid(row=1, column=0, sticky=tk.W)
        self.resolution_var = tk.StringVar(value="Media")
        resolution_combo = ttk.Combobox(left_frame, textvariable=self.resolution_var,
                                       values=["Baja", "Media", "Alta"])
        resolution_combo.grid(row=1, column=1, padx=(10, 0), pady=(0, 5))
        resolution_combo.state(['readonly'])
        
        # Configuraciones de la derecha
        ttk.Label(right_frame, text="Escala Z:").grid(row=0, column=0, sticky=tk.W)
        self.z_scale_var = tk.DoubleVar(value=1.0)
        z_scale_spin = ttk.Spinbox(right_frame, from_=0.1, to=10.0, increment=0.1,
                                  textvariable=self.z_scale_var, width=10)
        z_scale_spin.grid(row=0, column=1, padx=(10, 0), pady=(0, 5))
        
        ttk.Label(right_frame, text="Suavizado:").grid(row=1, column=0, sticky=tk.W)
        self.smoothing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_frame, variable=self.smoothing_var).grid(row=1, column=1, padx=(10, 0))
    
    def _create_processing_frame(self, parent):
        """Crea el frame de procesamiento."""
        process_frame = ttk.LabelFrame(parent, text="3. Procesamiento", padding="10")
        process_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones de procesamiento
        button_frame = ttk.Frame(process_frame)
        button_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(button_frame, text="Procesar Datos", 
                  command=self._process_data).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="Generar Malla 3D", 
                  command=self._generate_mesh).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exportar STL", 
                  command=self._export_stl).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(button_frame, text="Vista Previa", 
                  command=self._preview_model).grid(row=0, column=3)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(process_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        process_frame.columnconfigure(0, weight=1)
    
    def _create_log_frame(self, parent):
        """Crea el frame de registro."""
        log_frame = ttk.LabelFrame(parent, text="Registro de Actividad", padding="10")
        log_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget con scrollbar
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _setup_logging(self):
        """Configura el sistema de logging para mostrar en la interfaz."""
        # Crear un handler personalizado para la interfaz
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)
                self.text_widget.update()
        
        # Configurar el handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Agregar el handler al logger raíz
        logging.getLogger().addHandler(gui_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def _browse_dem_file(self):
        """Permite al usuario seleccionar un archivo DEM."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo DEM",
            filetypes=[
                ("Archivos GeoTIFF", "*.tif *.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            logger.info(f"Archivo seleccionado: {file_path}")
    
    def _load_dem_file(self):
        """Carga el archivo DEM seleccionado."""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Por favor seleccione un archivo DEM")
            return
        
        self.status_var.set("Cargando archivo DEM...")
        self.progress_var.set(10)
        
        try:
            success = self.dem_loader.load_dem_file(file_path)
            
            if success:
                metadata = self.dem_loader.get_metadata()
                self.current_dem_data = self.dem_loader.get_elevation_data()
                
                info_text = (f"Archivo cargado: {metadata['shape'][0]}x{metadata['shape'][1]} puntos, "
                           f"Elevación: {metadata['min_elevation']:.1f} - {metadata['max_elevation']:.1f}m")
                self.file_info_var.set(info_text)
                
                self.progress_var.set(100)
                self.status_var.set("Archivo DEM cargado exitosamente")
                logger.info("Archivo DEM cargado exitosamente")
            else:
                messagebox.showerror("Error", "No se pudo cargar el archivo DEM")
                self.status_var.set("Error al cargar archivo")
                
        except Exception as e:
            logger.error(f"Error al cargar DEM: {e}")
            messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")
            self.status_var.set("Error al cargar archivo")
        
        self.progress_var.set(0)
    
    def _process_data(self):
        """Procesa los datos DEM cargados."""
        if self.current_dem_data is None:
            messagebox.showerror("Error", "Primero debe cargar un archivo DEM")
            return
        
        self.status_var.set("Procesando datos...")
        logger.info("Iniciando procesamiento de datos")
        
        # Implementación pendiente
        messagebox.showinfo("Información", "Funcionalidad de procesamiento en desarrollo")
        self.status_var.set("Listo")
    
    def _generate_mesh(self):
        """Genera la malla 3D."""
        messagebox.showinfo("Información", "Funcionalidad de generación de malla en desarrollo")
    
    def _export_stl(self):
        """Exporta el modelo a formato STL."""
        messagebox.showinfo("Información", "Funcionalidad de exportación STL en desarrollo")
    
    def _preview_model(self):
        """Muestra una vista previa del modelo."""
        messagebox.showinfo("Información", "Funcionalidad de vista previa en desarrollo")
    
    def run(self):
        """Inicia la aplicación."""
        logger.info("Iniciando aplicación Mapa 3D del Ecuador")
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
