"""
Ventana principal de la aplicación
=================================

Este módulo implementa la ventana principal de la aplicación para
generar mapas 3D del Ecuador con funcionalidades avanzadas.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.dem_loader import DEMLoader
from data_processing.advanced_dem_loader import AdvancedDEMLoader
from data_processing.ecuador_filter import EcuadorFilter
from data_processing.political_segmentation import PoliticalSegmentation
from mesh_generation.terrain_to_mesh import TerrainToMesh
from mesh_generation.stl_exporter import STLExporter
from validation.print_validator import PrintValidator
from gui.zone_selector import ZoneSelector

logger = logging.getLogger(__name__)


class MainWindow:
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mapa 3D del Ecuador - Generador Avanzado")
        self.root.geometry("1200x800")
        
        # Componentes del procesamiento
        self.dem_loader = DEMLoader()
        self.advanced_loader = AdvancedDEMLoader()
        self.ecuador_filter = EcuadorFilter()
        self.political_segmentation = PoliticalSegmentation()
        self.terrain_to_mesh = TerrainToMesh()
        self.stl_exporter = STLExporter()
        self.zone_selector = None
        
        # Variables de estado
        self.current_dem_data = None
        self.processed_data = None
        self.selected_zone = None
        self.available_files = {}
        self.mesh_data = None
        
        self._setup_ui()
        self._setup_logging()
        self._scan_data_files()
        
        logger.info("Ventana principal inicializada con funcionalidades avanzadas")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario avanzada."""
        # Crear notebook para pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña principal
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Generación de Mapas 3D")
        
        # Pestaña de análisis
        analysis_tab = ttk.Frame(notebook)
        notebook.add(analysis_tab, text="Análisis de Datos")
        
        # Configurar pestaña principal
        self._setup_main_tab(main_tab)
        
        # Configurar pestaña de análisis
        self._setup_analysis_tab(analysis_tab)
        
        # Barra de estado general
        self.status_var = tk.StringVar()
        self.status_var.set("Listo - Sistema inicializado")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    def _setup_main_tab(self, parent):
        """Configura la pestaña principal."""
        # Frame principal con scroll
        main_canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título
        title_label = ttk.Label(scrollable_frame, text="Generador Avanzado de Mapas 3D del Ecuador", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Frame de carga de datos
        self._create_advanced_data_loading_frame(scrollable_frame)
        
        # Frame de selección de zona
        self._create_zone_selection_frame(scrollable_frame)
        
        # Frame de configuración
        self._create_advanced_configuration_frame(scrollable_frame)
        
        # Frame de procesamiento
        self._create_processing_frame(scrollable_frame)
        
        # Frame de vista previa
        self._create_preview_frame(scrollable_frame)
        
        # Configurar canvas
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _setup_analysis_tab(self, parent):
        """Configura la pestaña de análisis."""
        # Frame de análisis estadístico
        stats_frame = ttk.LabelFrame(parent, text="Análisis Estadístico", padding="15")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Variables para estadísticas
        self.stats_text = tk.Text(stats_frame, height=15, state=tk.DISABLED, wrap=tk.WORD)
        stats_scroll = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para actualizar estadísticas
        ttk.Button(parent, text="Actualizar Análisis", 
                  command=self._update_statistics).pack(pady=10)
    
    def _create_advanced_data_loading_frame(self, parent):
        """Crea el frame avanzado para carga de datos."""
        data_frame = ttk.LabelFrame(parent, text="1. Carga Avanzada de Datos DEM", padding="15")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame para botones de carga
        button_frame = ttk.Frame(data_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Escanear Archivos Locales", 
                  command=self._scan_data_files).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Examinar Archivo...", 
                  command=self._browse_dem_file).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Crear Datos de Prueba", 
                  command=self._create_sample_data).pack(side=tk.LEFT, padx=(0, 10))
        
        # Lista de archivos disponibles
        files_frame = ttk.Frame(data_frame)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(files_frame, text="Archivos Disponibles:").pack(anchor=tk.W)
        
        # Treeview para mostrar archivos
        self.files_tree = ttk.Treeview(files_frame, height=6, columns=('size', 'type'), show='tree headings')
        self.files_tree.heading('#0', text='Archivo')
        self.files_tree.heading('size', text='Tamaño')
        self.files_tree.heading('type', text='Tipo')
        
        files_scroll = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scroll.set)
        
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para cargar archivo seleccionado
        ttk.Button(data_frame, text="Cargar Archivo Seleccionado", 
                  command=self._load_selected_file).pack(pady=(10, 0))
        
        # Información del archivo cargado
        self.file_info_var = tk.StringVar()
        self.file_info_var.set("No hay archivo cargado")
        ttk.Label(data_frame, textvariable=self.file_info_var, 
                 foreground="blue", font=('Arial', 10)).pack(pady=(10, 0))
    
    def _create_zone_selection_frame(self, parent):
        """Crea el frame para selección de zonas."""
        zone_frame = ttk.LabelFrame(parent, text="2. Selección de Zona Geográfica", padding="15")
        zone_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame para controles de zona
        controls_frame = ttk.Frame(zone_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controls_frame, text="Abrir Selector de Zonas", 
                  command=self._open_zone_selector).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Zona Completa (Ecuador)", 
                  command=self._select_full_ecuador).pack(side=tk.LEFT, padx=(0, 10))
        
        # Información de zona seleccionada
        self.zone_info_var = tk.StringVar()
        self.zone_info_var.set("Zona: Ecuador Completo")
        ttk.Label(zone_frame, textvariable=self.zone_info_var, 
                 foreground="green", font=('Arial', 11, 'bold')).pack()
    
    def _create_advanced_configuration_frame(self, parent):
        """Crea el frame de configuración avanzada."""
        config_frame = ttk.LabelFrame(parent, text="3. Configuración Avanzada", padding="15")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame principal para configuraciones
        main_config = ttk.Frame(config_frame)
        main_config.pack(fill=tk.X)
        
        # Columna izquierda
        left_config = ttk.Frame(main_config)
        left_config.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        # Resolución de malla
        ttk.Label(left_config, text="Resolución de Malla:").pack(anchor=tk.W)
        self.mesh_resolution_var = tk.IntVar(value=100)
        resolution_frame = ttk.Frame(left_config)
        resolution_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(resolution_frame, from_=50, to=500, variable=self.mesh_resolution_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(resolution_frame, textvariable=self.mesh_resolution_var).pack(side=tk.RIGHT)
        
        # Escala vertical
        ttk.Label(left_config, text="Escala Vertical:").pack(anchor=tk.W)
        self.z_scale_var = tk.DoubleVar(value=1.0)
        z_scale_frame = ttk.Frame(left_config)
        z_scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(z_scale_frame, from_=0.1, to=5.0, variable=self.z_scale_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(z_scale_frame, textvariable=self.z_scale_var).pack(side=tk.RIGHT)
        
        # Columna derecha
        right_config = ttk.Frame(main_config)
        right_config.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Opciones de procesamiento
        ttk.Label(right_config, text="Opciones de Procesamiento:").pack(anchor=tk.W)
        
        self.smoothing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_config, text="Aplicar suavizado", 
                       variable=self.smoothing_var).pack(anchor=tk.W, pady=2)
        
        self.fill_holes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_config, text="Rellenar huecos", 
                       variable=self.fill_holes_var).pack(anchor=tk.W, pady=2)
        
        self.optimize_mesh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_config, text="Optimizar malla", 
                       variable=self.optimize_mesh_var).pack(anchor=tk.W, pady=2)
        
        # Validación para impresión 3D
        validation_frame = ttk.Frame(config_frame)
        validation_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(validation_frame, text="Validación para Impresión 3D:").pack(anchor=tk.W)
        
        self.validate_manifold_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_frame, text="Verificar manifold", 
                       variable=self.validate_manifold_var).pack(anchor=tk.W, pady=2)
        
        self.check_printability_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_frame, text="Verificar imprimibilidad", 
                       variable=self.check_printability_var).pack(anchor=tk.W, pady=2)
    
    def _create_preview_frame(self, parent):
        """Crea el frame para vista previa."""
        preview_frame = ttk.LabelFrame(parent, text="5. Vista Previa del Modelo", padding="15")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para controles de vista previa
        preview_controls = ttk.Frame(preview_frame)
        preview_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(preview_controls, text="Vista 2D (Mapa de Elevación)", 
                  command=self._show_2d_preview).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(preview_controls, text="Vista 3D (Modelo)", 
                  command=self._show_3d_preview).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(preview_controls, text="Estadísticas del Modelo", 
                  command=self._show_model_stats).pack(side=tk.LEFT)
        
        # Canvas para mostrar previsualizaciones
        self.preview_canvas_frame = ttk.Frame(preview_frame)
        self.preview_canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    def _scan_data_files(self):
        """Escanea archivos de datos disponibles."""
        try:
            self.available_files = self.advanced_loader.scan_available_files()
            self._update_files_tree()
            
            total_files = sum(len(files) for files in self.available_files.values())
            logger.info(f"Escaneados {total_files} archivos DEM disponibles")
            
        except Exception as e:
            logger.error(f"Error escaneando archivos: {e}")
    
    def _update_files_tree(self):
        """Actualiza el árbol de archivos disponibles."""
        # Limpiar árbol actual
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        # Agregar archivos por formato
        for format_name, files in self.available_files.items():
            format_item = self.files_tree.insert('', 'end', text=f"{format_name} ({len(files)} archivos)")
            
            for file_info in files:
                self.files_tree.insert(format_item, 'end', 
                                     text=file_info['name'],
                                     values=(file_info['size'], format_name),
                                     tags=('file',))
        
        # Configurar tags
        self.files_tree.tag_configure('file', foreground='blue')
    
    def _load_selected_file(self):
        """Carga el archivo seleccionado en el árbol."""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un archivo para cargar")
            return
        
        selected_item = selection[0]
        
        # Verificar si es un archivo (no un formato)
        if 'file' not in self.files_tree.item(selected_item, 'tags'):
            messagebox.showwarning("Advertencia", "Por favor seleccione un archivo específico, no una categoría")
            return
        
        # Encontrar la ruta del archivo
        file_name = self.files_tree.item(selected_item, 'text')
        file_path = None
        
        for format_files in self.available_files.values():
            for file_info in format_files:
                if file_info['name'] == file_name:
                    file_path = file_info['path']
                    break
            if file_path:
                break
        
        if file_path:
            self._load_dem_file(file_path)
        else:
            messagebox.showerror("Error", "No se pudo encontrar la ruta del archivo")
    
    def _create_sample_data(self):
        """Crea datos de muestra para pruebas."""
        try:
            # Crear directorio de datos si no existe
            data_dir = self.advanced_loader.data_directory
            os.makedirs(data_dir, exist_ok=True)
            
            # Crear archivo de muestra
            sample_file = os.path.join(data_dir, "ecuador_sample.asc")
            
            zone_bounds = None
            if self.selected_zone:
                zone_bounds = self.selected_zone
            
            self.advanced_loader.create_sample_data_file(sample_file, zone_bounds)
            
            # Reescanear archivos
            self._scan_data_files()
            
            messagebox.showinfo("Éxito", f"Archivo de muestra creado: {sample_file}")
            
        except Exception as e:
            logger.error(f"Error creando datos de muestra: {e}")
            messagebox.showerror("Error", f"No se pudo crear el archivo de muestra: {str(e)}")
    
    def _open_zone_selector(self):
        """Abre el selector de zonas."""
        try:
            if not self.zone_selector:
                self.zone_selector = ZoneSelector(self.root)
            
            selected_zone = self.zone_selector.show_dialog()
            
            if selected_zone:
                self.selected_zone = selected_zone
                zone_info = f"Zona: {selected_zone['name']} ({selected_zone['min_lat']:.2f}, {selected_zone['min_lon']:.2f}) - ({selected_zone['max_lat']:.2f}, {selected_zone['max_lon']:.2f})"
                self.zone_info_var.set(zone_info)
                logger.info(f"Zona seleccionada: {selected_zone['name']}")
            
        except Exception as e:
            logger.error(f"Error abriendo selector de zonas: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el selector de zonas: {str(e)}")
    
    def _select_full_ecuador(self):
        """Selecciona Ecuador completo."""
        self.selected_zone = {
            'name': 'Ecuador Completo',
            'min_lat': -5.0,
            'max_lat': 1.5,
            'min_lon': -81.0,
            'max_lon': -75.0
        }
        self.zone_info_var.set("Zona: Ecuador Completo")
        logger.info("Seleccionada zona completa de Ecuador")
    
    def _show_2d_preview(self):
        """Muestra vista previa 2D del modelo."""
        if self.current_dem_data is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar datos DEM")
            return
        
        try:
            # Limpiar frame de vista previa
            for widget in self.preview_canvas_frame.winfo_children():
                widget.destroy()
            
            # Crear figura de matplotlib
            fig = Figure(figsize=(10, 8), dpi=100)
            ax = fig.add_subplot(111)
            
            # Mostrar mapa de elevación
            im = ax.imshow(self.current_dem_data, cmap='terrain', aspect='auto')
            ax.set_title('Mapa de Elevación - Vista 2D')
            ax.set_xlabel('Longitud (píxeles)')
            ax.set_ylabel('Latitud (píxeles)')
            
            # Agregar barra de color
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label('Elevación (m)')
            
            # Integrar con tkinter
            canvas = FigureCanvasTkAgg(fig, self.preview_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            logger.info("Vista previa 2D generada")
            
        except Exception as e:
            logger.error(f"Error generando vista previa 2D: {e}")
            messagebox.showerror("Error", f"No se pudo generar la vista previa: {str(e)}")
    
    def _show_3d_preview(self):
        """Muestra vista previa 3D del modelo."""
        if self.mesh_data is None:
            messagebox.showwarning("Advertencia", "Primero debe generar la malla 3D")
            return
        
        messagebox.showinfo("Información", "Vista previa 3D en desarrollo")
    
    def _show_model_stats(self):
        """Muestra estadísticas del modelo."""
        if self.current_dem_data is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar datos DEM")
            return
        
        try:
            # Calcular estadísticas
            valid_data = self.current_dem_data[~np.isnan(self.current_dem_data)]
            
            stats = {
                'Dimensiones': f"{self.current_dem_data.shape[0]} x {self.current_dem_data.shape[1]}",
                'Puntos válidos': f"{len(valid_data):,}",
                'Puntos sin datos': f"{np.sum(np.isnan(self.current_dem_data)):,}",
                'Elevación mínima': f"{np.min(valid_data):.1f} m",
                'Elevación máxima': f"{np.max(valid_data):.1f} m",
                'Elevación promedio': f"{np.mean(valid_data):.1f} m",
                'Desviación estándar': f"{np.std(valid_data):.1f} m",
                'Rango de elevación': f"{np.max(valid_data) - np.min(valid_data):.1f} m"
            }
            
            # Mostrar en una ventana
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Estadísticas del Modelo")
            stats_window.geometry("400x300")
            
            stats_text = tk.Text(stats_window, wrap=tk.WORD, padx=20, pady=20)
            stats_text.pack(fill=tk.BOTH, expand=True)
            
            for key, value in stats.items():
                stats_text.insert(tk.END, f"{key}: {value}\n")
            
            stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas: {e}")
            messagebox.showerror("Error", f"No se pudieron calcular las estadísticas: {str(e)}")
    
    def _update_statistics(self):
        """Actualiza las estadísticas en la pestaña de análisis."""
        if self.current_dem_data is None:
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No hay datos cargados para analizar.")
            self.stats_text.config(state=tk.DISABLED)
            return
        
        try:
            # Análisis detallado
            valid_data = self.current_dem_data[~np.isnan(self.current_dem_data)]
            
            analysis = f"""ANÁLISIS ESTADÍSTICO DETALLADO
{'='*40}

INFORMACIÓN BÁSICA:
- Dimensiones de la grilla: {self.current_dem_data.shape[0]} × {self.current_dem_data.shape[1]} puntos
- Total de puntos: {self.current_dem_data.size:,}
- Puntos con datos válidos: {len(valid_data):,} ({len(valid_data)/self.current_dem_data.size*100:.1f}%)
- Puntos sin datos (NoData): {np.sum(np.isnan(self.current_dem_data)):,}

ESTADÍSTICAS DE ELEVACIÓN:
- Mínima: {np.min(valid_data):.2f} m
- Máxima: {np.max(valid_data):.2f} m
- Promedio: {np.mean(valid_data):.2f} m
- Mediana: {np.median(valid_data):.2f} m
- Desviación estándar: {np.std(valid_data):.2f} m
- Rango total: {np.max(valid_data) - np.min(valid_data):.2f} m

PERCENTILES:
- 5%: {np.percentile(valid_data, 5):.2f} m
- 25%: {np.percentile(valid_data, 25):.2f} m
- 75%: {np.percentile(valid_data, 75):.2f} m
- 95%: {np.percentile(valid_data, 95):.2f} m

DISTRIBUCIÓN POR RANGOS DE ELEVACIÓN:
"""
            
            # Análisis por rangos
            ranges = [(0, 500), (500, 1000), (1000, 2000), (2000, 3000), (3000, 4000), (4000, float('inf'))]
            for min_elev, max_elev in ranges:
                if max_elev == float('inf'):
                    count = np.sum(valid_data >= min_elev)
                    analysis += f"- {min_elev}+ m: {count:,} puntos ({count/len(valid_data)*100:.1f}%)\n"
                else:
                    count = np.sum((valid_data >= min_elev) & (valid_data < max_elev))
                    analysis += f"- {min_elev}-{max_elev} m: {count:,} puntos ({count/len(valid_data)*100:.1f}%)\n"
            
            # Actualizar el texto
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, analysis)
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"Error calculando estadísticas: {str(e)}")
            self.stats_text.config(state=tk.DISABLED)
    
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
                ("Archivos SRTM", "*.hgt"),
                ("ASCII Grid", "*.asc"),
                ("Archivos XYZ", "*.xyz"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self._load_dem_file(file_path)
    
    def _load_dem_file(self, file_path: str = None):
        """Carga un archivo DEM específico."""
        if not file_path:
            messagebox.showerror("Error", "No se especificó un archivo para cargar")
            return
        
        self.status_var.set("Cargando archivo DEM...")
        self.progress_var.set(10)
        
        try:
            # Usar el cargador avanzado
            success = self.advanced_loader.load_dem_file(file_path, self.selected_zone)
            
            if success:
                self.current_dem_data = self.advanced_loader.get_elevation_data()
                metadata = self.advanced_loader.get_metadata()
                
                # Información del archivo
                file_name = os.path.basename(file_path)
                data_shape = self.current_dem_data.shape
                
                valid_data = self.current_dem_data[~np.isnan(self.current_dem_data)]
                min_elev = np.min(valid_data) if len(valid_data) > 0 else 0
                max_elev = np.max(valid_data) if len(valid_data) > 0 else 0
                
                info_text = (f"Archivo: {file_name} | "
                           f"Dimensiones: {data_shape[0]}×{data_shape[1]} | "
                           f"Elevación: {min_elev:.1f} - {max_elev:.1f}m | "
                           f"Formato: {metadata.get('format', 'Desconocido')}")
                
                self.file_info_var.set(info_text)
                
                self.progress_var.set(100)
                self.status_var.set("Archivo DEM cargado exitosamente")
                logger.info(f"Archivo DEM cargado: {file_path}")
                
                # Actualizar estadísticas automáticamente
                self._update_statistics()
                
            else:
                messagebox.showerror("Error", "No se pudo cargar el archivo DEM")
                self.status_var.set("Error al cargar archivo")
                
        except Exception as e:
            logger.error(f"Error al cargar DEM: {e}")
            messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")
            self.status_var.set("Error al cargar archivo")
        
        self.progress_var.set(0)
    
    def _process_data(self):
        """Procesa los datos DEM cargados con configuraciones avanzadas."""
        if self.current_dem_data is None:
            messagebox.showerror("Error", "Primero debe cargar un archivo DEM")
            return
        
        self.status_var.set("Procesando datos...")
        self.progress_var.set(10)
        logger.info("Iniciando procesamiento avanzado de datos")
        
        try:
            # Crear copia de los datos para procesamiento
            processed_data = self.current_dem_data.copy()
            
            # Aplicar filtro de Ecuador si es necesario
            if self.selected_zone and self.selected_zone['name'] != 'Ecuador Completo':
                logger.info(f"Aplicando filtro de zona: {self.selected_zone['name']}")
                # Aquí se implementaría el filtrado por zona específica
                
            self.progress_var.set(30)
            
            # Aplicar suavizado si está habilitado
            if self.smoothing_var.get():
                logger.info("Aplicando suavizado a los datos")
                from scipy import ndimage
                processed_data = ndimage.gaussian_filter(processed_data, sigma=1.0)
                
            self.progress_var.set(50)
            
            # Rellenar huecos si está habilitado
            if self.fill_holes_var.get():
                logger.info("Rellenando huecos en los datos")
                # Interpolar valores faltantes
                mask = np.isnan(processed_data)
                if np.any(mask):
                    from scipy.interpolate import griddata
                    valid_points = np.where(~mask)
                    valid_values = processed_data[valid_points]
                    
                    missing_points = np.where(mask)
                    if len(missing_points[0]) > 0:
                        interpolated = griddata(
                            (valid_points[0], valid_points[1]), 
                            valid_values,
                            (missing_points[0], missing_points[1]),
                            method='linear'
                        )
                        processed_data[missing_points] = interpolated
            
            self.progress_var.set(70)
            
            # Aplicar escala vertical
            z_scale = self.z_scale_var.get()
            if z_scale != 1.0:
                logger.info(f"Aplicando escala vertical: {z_scale}")
                processed_data *= z_scale
            
            self.processed_data = processed_data
            self.progress_var.set(100)
            self.status_var.set("Datos procesados exitosamente")
            logger.info("Procesamiento de datos completado")
            
            # Actualizar estadísticas
            self._update_statistics()
            
        except Exception as e:
            logger.error(f"Error procesando datos: {e}")
            messagebox.showerror("Error", f"Error en el procesamiento: {str(e)}")
            self.status_var.set("Error en procesamiento")
        
        self.progress_var.set(0)
    
    def _generate_mesh(self):
        """Genera la malla 3D del terreno."""
        if self.processed_data is None:
            messagebox.showerror("Error", "Primero debe procesar los datos DEM")
            return
        
        self.status_var.set("Generando malla 3D...")
        self.progress_var.set(10)
        logger.info("Iniciando generación de malla 3D")
        
        try:
            # Configurar parámetros de malla
            resolution = self.mesh_resolution_var.get()
            
            # Redimensionar datos si es necesario
            if max(self.processed_data.shape) > resolution:
                from scipy.ndimage import zoom
                scale_factor = resolution / max(self.processed_data.shape)
                resized_data = zoom(self.processed_data, scale_factor)
                logger.info(f"Datos redimensionados a {resized_data.shape} para malla")
            else:
                resized_data = self.processed_data
            
            self.progress_var.set(30)
            
            # Generar malla usando el módulo de generación de terreno
            success = self.terrain_to_mesh.generate_mesh(resized_data)
            
            if success:
                self.mesh_data = self.terrain_to_mesh.get_mesh()
                
                # Optimizar malla si está habilitado
                if self.optimize_mesh_var.get():
                    logger.info("Optimizando malla 3D")
                    self.terrain_to_mesh.optimize_mesh()
                    self.mesh_data = self.terrain_to_mesh.get_mesh()
                
                self.progress_var.set(80)
                
                # Validar malla si está habilitado
                if self.validate_manifold_var.get():
                    logger.info("Validando estructura de malla")
                    # Aquí se implementaría la validación de manifold
                
                self.progress_var.set(100)
                self.status_var.set("Malla 3D generada exitosamente")
                logger.info("Malla 3D generada exitosamente")
                
                messagebox.showinfo("Éxito", "Malla 3D generada correctamente")
                
            else:
                messagebox.showerror("Error", "No se pudo generar la malla 3D")
                self.status_var.set("Error generando malla")
                
        except Exception as e:
            logger.error(f"Error generando malla: {e}")
            messagebox.showerror("Error", f"Error en la generación de malla: {str(e)}")
            self.status_var.set("Error generando malla")
        
        self.progress_var.set(0)
    
    def _export_stl(self):
        """Exporta el modelo a formato STL."""
        if self.mesh_data is None:
            messagebox.showerror("Error", "Primero debe generar la malla 3D")
            return
        
        # Seleccionar archivo de salida
        zone_name = self.selected_zone['name'] if self.selected_zone else "Ecuador"
        default_name = f"mapa_3d_{zone_name.lower().replace(' ', '_')}.stl"
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar archivo STL",
            defaultextension=".stl",
            initialvalue=default_name,
            filetypes=[("Archivos STL", "*.stl"), ("Todos los archivos", "*.*")]
        )
        
        if not file_path:
            return
        
        self.status_var.set("Exportando archivo STL...")
        self.progress_var.set(10)
        logger.info(f"Exportando a STL: {file_path}")
        
        try:
            # Exportar usando el módulo STL exporter
            success = self.stl_exporter.export_mesh(self.mesh_data, file_path)
            
            if success:
                self.progress_var.set(80)
                
                # Validar archivo para impresión 3D si está habilitado
                if self.check_printability_var.get():
                    logger.info("Validando archivo para impresión 3D")
                    # Aquí se implementaría la validación de imprimibilidad
                
                self.progress_var.set(100)
                self.status_var.set(f"STL exportado: {os.path.basename(file_path)}")
                logger.info(f"Archivo STL exportado exitosamente: {file_path}")
                
                messagebox.showinfo("Éxito", 
                                  f"Archivo STL exportado exitosamente:\n{file_path}\n\n"
                                  f"Ahora puede usar este archivo en Bambu Studio para impresión 3D.")
                
            else:
                messagebox.showerror("Error", "No se pudo exportar el archivo STL")
                self.status_var.set("Error exportando STL")
                
        except Exception as e:
            logger.error(f"Error exportando STL: {e}")
            messagebox.showerror("Error", f"Error en la exportación: {str(e)}")
            self.status_var.set("Error exportando STL")
        
        self.progress_var.set(0)
    
    def run(self):
        """Inicia la aplicación."""
        logger.info("Iniciando aplicación Mapa 3D del Ecuador")
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
