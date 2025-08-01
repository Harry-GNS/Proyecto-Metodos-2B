"""
Selector de zonas geográficas
============================

Este módulo implementa un selector avanzado de zonas geográficas
del Ecuador para procesamiento específico.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class ZoneSelector:
    """Selector avanzado de zonas geográficas del Ecuador."""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.selected_zone = None
        self.custom_bounds = None
        
        # Definir zonas predefinidas
        self.predefined_zones = {
            "Ecuador Completo": {
                "bounds": {"min_lat": -5.0, "max_lat": 1.5, "min_lon": -81.0, "max_lon": -75.0},
                "description": "Todo el territorio continental del Ecuador",
                "provinces": "Todas las provincias continentales"
            },
            "Región Costa": {
                "bounds": {"min_lat": -5.0, "max_lat": 1.5, "min_lon": -81.0, "max_lon": -79.0},
                "description": "Región costera del Pacífico",
                "provinces": "Esmeraldas, Manabí, Los Ríos, Guayas, Santa Elena, El Oro"
            },
            "Región Sierra": {
                "bounds": {"min_lat": -5.0, "max_lat": 1.5, "min_lon": -79.0, "max_lon": -77.5},
                "description": "Cordillera de los Andes",
                "provinces": "Carchi, Imbabura, Pichincha, Cotopaxi, Tungurahua, Chimborazo, Bolívar, Cañar, Azuay, Loja"
            },
            "Región Oriente": {
                "bounds": {"min_lat": -5.0, "max_lat": 1.5, "min_lon": -77.5, "max_lon": -75.0},
                "description": "Selva amazónica ecuatoriana",
                "provinces": "Sucumbíos, Napo, Orellana, Pastaza, Morona Santiago, Zamora Chinchipe"
            },
            "Norte del Ecuador": {
                "bounds": {"min_lat": -1.0, "max_lat": 1.5, "min_lon": -81.0, "max_lon": -75.0},
                "description": "Provincias del norte",
                "provinces": "Carchi, Imbabura, Esmeraldas, Sucumbíos"
            },
            "Centro del Ecuador": {
                "bounds": {"min_lat": -2.5, "max_lat": -0.5, "min_lon": -81.0, "max_lon": -75.0},
                "description": "Provincias centrales",
                "provinces": "Pichincha, Cotopaxi, Tungurahua, Chimborazo, Los Ríos, Manabí"
            },
            "Sur del Ecuador": {
                "bounds": {"min_lat": -5.0, "max_lat": -2.0, "min_lon": -81.0, "max_lon": -75.0},
                "description": "Provincias del sur",
                "provinces": "Azuay, Cañar, Loja, El Oro, Zamora Chinchipe"
            },
            "Volcanes Principales": {
                "bounds": {"min_lat": -2.0, "max_lat": 1.0, "min_lon": -79.5, "max_lon": -78.0},
                "description": "Área de volcanes principales (Cotopaxi, Chimborazo, etc.)",
                "provinces": "Cotopaxi, Tungurahua, Chimborazo"
            },
            "Guayaquil y Alrededores": {
                "bounds": {"min_lat": -3.0, "max_lat": -1.5, "min_lon": -80.5, "max_lon": -79.0},
                "description": "Área metropolitana de Guayaquil",
                "provinces": "Guayas, Los Ríos (parte)"
            },
            "Quito y Alrededores": {
                "bounds": {"min_lat": -0.5, "max_lat": 0.5, "min_lon": -79.0, "max_lon": -78.0},
                "description": "Área metropolitana de Quito",
                "provinces": "Pichincha"
            }
        }
        
        self._create_zone_selector_ui()
    
    def _create_zone_selector_ui(self):
        """Crea la interfaz del selector de zonas."""
        # Frame principal
        main_frame = ttk.LabelFrame(self.parent_frame, text="Selección de Zona Geográfica", padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        main_frame.columnconfigure(1, weight=1)
        
        # Selector de zona predefinida
        ttk.Label(main_frame, text="Zona:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.zone_var = tk.StringVar(value="Ecuador Completo")
        zone_combo = ttk.Combobox(main_frame, textvariable=self.zone_var, 
                                 values=list(self.predefined_zones.keys()),
                                 width=30)
        zone_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        zone_combo.bind('<<ComboboxSelected>>', self._on_zone_selected)
        zone_combo.state(['readonly'])
        
        # Botón para zona personalizada
        ttk.Button(main_frame, text="Zona Personalizada...", 
                  command=self._open_custom_zone_dialog).grid(row=0, column=2)
        
        # Información de la zona seleccionada
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(0, weight=1)
        
        self.zone_info_var = tk.StringVar()
        self.zone_info_label = ttk.Label(info_frame, textvariable=self.zone_info_var, 
                                        wraplength=600, justify=tk.LEFT,
                                        foreground="blue")
        self.zone_info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Coordenadas de la zona
        coords_frame = ttk.Frame(main_frame)
        coords_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.coords_info_var = tk.StringVar()
        coords_label = ttk.Label(coords_frame, textvariable=self.coords_info_var, 
                                font=('Courier', 9), foreground="darkgreen")
        coords_label.grid(row=0, column=0, sticky=tk.W)
        
        # Inicializar con zona por defecto
        self._on_zone_selected()
    
    def _on_zone_selected(self, event=None):
        """Maneja la selección de una zona."""
        selected_zone = self.zone_var.get()
        
        if selected_zone in self.predefined_zones:
            zone_data = self.predefined_zones[selected_zone]
            self.selected_zone = selected_zone
            self.custom_bounds = None
            
            # Actualizar información
            info_text = f"📍 {zone_data['description']}\n🏛️ Provincias: {zone_data['provinces']}"
            self.zone_info_var.set(info_text)
            
            # Actualizar coordenadas
            bounds = zone_data['bounds']
            coords_text = (f"Coordenadas: {bounds['min_lat']}°S - {bounds['max_lat']}°N, "
                          f"{abs(bounds['min_lon'])}°W - {abs(bounds['max_lon'])}°W")
            self.coords_info_var.set(coords_text)
            
            logger.info(f"Zona seleccionada: {selected_zone}")
    
    def _open_custom_zone_dialog(self):
        """Abre el diálogo para definir una zona personalizada."""
        dialog = CustomZoneDialog(self.parent_frame, self._on_custom_zone_defined)
    
    def _on_custom_zone_defined(self, bounds: Dict, name: str):
        """Maneja la definición de una zona personalizada."""
        self.custom_bounds = bounds
        self.selected_zone = f"Personalizada: {name}"
        
        # Actualizar información
        info_text = f"📍 Zona personalizada: {name}\n🎯 Área específica definida por el usuario"
        self.zone_info_var.set(info_text)
        
        # Actualizar coordenadas
        coords_text = (f"Coordenadas: {bounds['min_lat']}° - {bounds['max_lat']}°, "
                      f"{bounds['min_lon']}° - {bounds['max_lon']}°")
        self.coords_info_var.set(coords_text)
        
        # Actualizar selector
        self.zone_var.set(self.selected_zone)
        
        logger.info(f"Zona personalizada definida: {name}")
    
    def get_selected_bounds(self) -> Dict:
        """
        Retorna las coordenadas de la zona seleccionada.
        
        Returns:
            Dict: Diccionario con límites geográficos
        """
        if self.custom_bounds:
            return self.custom_bounds
        
        selected_zone = self.zone_var.get()
        if selected_zone in self.predefined_zones:
            return self.predefined_zones[selected_zone]['bounds']
        
        # Por defecto, Ecuador completo
        return self.predefined_zones['Ecuador Completo']['bounds']
    
    def get_zone_name(self) -> str:
        """Retorna el nombre de la zona seleccionada."""
        return self.selected_zone or self.zone_var.get()


class CustomZoneDialog:
    """Diálogo para definir una zona personalizada."""
    
    def __init__(self, parent, callback):
        self.callback = callback
        
        # Crear ventana del diálogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Definir Zona Personalizada")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar el diálogo
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self._create_dialog_ui()
    
    def _create_dialog_ui(self):
        """Crea la interfaz del diálogo."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Definir Zona Personalizada", 
                               font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Nombre de la zona
        ttk.Label(main_frame, text="Nombre de la zona:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value="Mi Zona")
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Coordenadas
        coords_frame = ttk.LabelFrame(main_frame, text="Límites Geográficos", padding="10")
        coords_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        coords_frame.columnconfigure(1, weight=1)
        coords_frame.columnconfigure(3, weight=1)
        
        # Latitud
        ttk.Label(coords_frame, text="Latitud Norte:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_lat_var = tk.DoubleVar(value=1.5)
        max_lat_spin = ttk.Spinbox(coords_frame, from_=-10, to=10, increment=0.1,
                                  textvariable=self.max_lat_var, width=10)
        max_lat_spin.grid(row=0, column=1, padx=(10, 20), pady=5)
        
        ttk.Label(coords_frame, text="Latitud Sur:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.min_lat_var = tk.DoubleVar(value=-5.0)
        min_lat_spin = ttk.Spinbox(coords_frame, from_=-10, to=10, increment=0.1,
                                  textvariable=self.min_lat_var, width=10)
        min_lat_spin.grid(row=0, column=3, padx=(10, 0), pady=5)
        
        # Longitud
        ttk.Label(coords_frame, text="Longitud Oeste (min):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.min_lon_var = tk.DoubleVar(value=-81.0)
        min_lon_spin = ttk.Spinbox(coords_frame, from_=-90, to=-70, increment=0.1,
                                  textvariable=self.min_lon_var, width=10)
        min_lon_spin.grid(row=1, column=1, padx=(10, 20), pady=5)
        
        ttk.Label(coords_frame, text="Longitud Este (max):").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.max_lon_var = tk.DoubleVar(value=-75.0)
        max_lon_spin = ttk.Spinbox(coords_frame, from_=-90, to=-70, increment=0.1,
                                  textvariable=self.max_lon_var, width=10)
        max_lon_spin.grid(row=1, column=3, padx=(10, 0), pady=5)
        
        # Ayuda
        help_frame = ttk.Frame(main_frame)
        help_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        help_text = ("💡 Consejos:\n"
                    "• Latitud: valores positivos = Norte, negativos = Sur\n"
                    "• Longitud: valores negativos para el hemisferio oeste\n"
                    "• Ecuador está entre 1.5°N y 5°S, 81°W y 75°W")
        
        help_label = ttk.Label(help_frame, text=help_text, 
                              foreground="blue", wraplength=450, justify=tk.LEFT)
        help_label.grid(row=0, column=0, sticky=tk.W)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.dialog.destroy).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="Definir Zona", 
                  command=self._define_zone).grid(row=0, column=1)
        
        # Vista previa
        preview_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding="10")
        preview_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.preview_var = tk.StringVar()
        preview_label = ttk.Label(preview_frame, textvariable=self.preview_var, 
                                 font=('Courier', 9), foreground="darkgreen")
        preview_label.grid(row=0, column=0, sticky=tk.W)
        
        # Actualizar vista previa inicialmente
        self._update_preview()
        
        # Bind para actualizar vista previa cuando cambien los valores
        for var in [self.name_var, self.min_lat_var, self.max_lat_var, self.min_lon_var, self.max_lon_var]:
            var.trace('w', lambda *args: self._update_preview())
    
    def _update_preview(self):
        """Actualiza la vista previa de la zona."""
        try:
            name = self.name_var.get()
            min_lat = self.min_lat_var.get()
            max_lat = self.max_lat_var.get()
            min_lon = self.min_lon_var.get()
            max_lon = self.max_lon_var.get()
            
            preview_text = (f"Zona: {name}\n"
                           f"Latitud: {min_lat}° a {max_lat}°\n"
                           f"Longitud: {min_lon}° a {max_lon}°\n"
                           f"Área aprox: {abs((max_lat - min_lat) * (max_lon - min_lon)):.2f} grados²")
            
            self.preview_var.set(preview_text)
        except tk.TclError:
            # Error en conversión de valores, ignorar
            pass
    
    def _define_zone(self):
        """Define la zona personalizada."""
        try:
            bounds = {
                'min_lat': self.min_lat_var.get(),
                'max_lat': self.max_lat_var.get(),
                'min_lon': self.min_lon_var.get(),
                'max_lon': self.max_lon_var.get()
            }
            
            name = self.name_var.get().strip()
            if not name:
                name = "Zona Personalizada"
            
            # Validar bounds
            if bounds['min_lat'] >= bounds['max_lat']:
                tk.messagebox.showerror("Error", "La latitud sur debe ser menor que la latitud norte")
                return
            
            if bounds['min_lon'] >= bounds['max_lon']:
                tk.messagebox.showerror("Error", "La longitud oeste debe ser menor que la longitud este")
                return
            
            # Llamar callback y cerrar diálogo
            self.callback(bounds, name)
            self.dialog.destroy()
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al definir zona: {e}")
