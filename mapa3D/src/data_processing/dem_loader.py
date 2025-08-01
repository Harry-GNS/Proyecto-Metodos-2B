"""
Cargador de archivos DEM (Digital Elevation Model)
=================================================

Este módulo proporciona funcionalidades para cargar y procesar archivos DEM
que contienen datos de elevación geográfica.
"""

import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DEMLoader:
    """Clase para cargar y procesar archivos DEM."""
    
    def __init__(self):
        self.dem_data = None
        self.transform = None
        self.crs = None
        self.bounds = None
    
    def load_dem_file(self, file_path):
        """
        Carga un archivo DEM desde el disco.
        
        Args:
            file_path (str): Ruta al archivo DEM
            
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            with rasterio.open(file_path) as src:
                self.dem_data = src.read(1)
                self.transform = src.transform
                self.crs = src.crs
                self.bounds = src.bounds
                
            logger.info(f"DEM cargado exitosamente: {file_path}")
            logger.info(f"Dimensiones: {self.dem_data.shape}")
            logger.info(f"Rango de elevaciones: {np.min(self.dem_data):.2f} - {np.max(self.dem_data):.2f} metros")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar DEM: {e}")
            return False
    
    def get_elevation_data(self):
        """
        Retorna los datos de elevación cargados.
        
        Returns:
            numpy.ndarray: Matriz de elevaciones
        """
        return self.dem_data
    
    def get_metadata(self):
        """
        Retorna metadatos del DEM.
        
        Returns:
            dict: Diccionario con metadatos
        """
        if self.dem_data is None:
            return None
            
        return {
            'shape': self.dem_data.shape,
            'transform': self.transform,
            'crs': self.crs,
            'bounds': self.bounds,
            'min_elevation': np.min(self.dem_data),
            'max_elevation': np.max(self.dem_data),
            'mean_elevation': np.mean(self.dem_data)
        }
    
    def apply_nodata_mask(self, nodata_value=-9999):
        """
        Aplica una máscara para valores NoData.
        
        Args:
            nodata_value: Valor que representa datos faltantes
        """
        if self.dem_data is not None:
            self.dem_data = np.where(self.dem_data == nodata_value, np.nan, self.dem_data)
            logger.info("Máscara NoData aplicada")
    
    def resample_dem(self, target_resolution):
        """
        Remuestrea el DEM a una resolución específica.
        
        Args:
            target_resolution (float): Resolución objetivo en metros
        """
        # Implementación pendiente
        logger.warning("Funcionalidad de remuestreo no implementada aún")
        pass
