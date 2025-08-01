"""
Filtros específicos para datos geográficos del Ecuador
====================================================

Este módulo implementa filtros y transformaciones específicas para
procesar datos geográficos del territorio ecuatoriano.
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import logging

logger = logging.getLogger(__name__)


class EcuadorFilter:
    """Clase para aplicar filtros específicos del Ecuador."""
    
    # Coordenadas aproximadas del Ecuador continental
    ECUADOR_BOUNDS = {
        'min_lat': -5.0,    # Sur
        'max_lat': 1.5,     # Norte  
        'min_lon': -81.0,   # Oeste
        'max_lon': -75.0    # Este
    }
    
    def __init__(self):
        self.ecuador_polygon = None
        self._create_ecuador_boundary()
    
    def _create_ecuador_boundary(self):
        """Crea un polígono aproximado de los límites del Ecuador."""
        coords = [
            (self.ECUADOR_BOUNDS['min_lon'], self.ECUADOR_BOUNDS['min_lat']),
            (self.ECUADOR_BOUNDS['max_lon'], self.ECUADOR_BOUNDS['min_lat']),
            (self.ECUADOR_BOUNDS['max_lon'], self.ECUADOR_BOUNDS['max_lat']),
            (self.ECUADOR_BOUNDS['min_lon'], self.ECUADOR_BOUNDS['max_lat']),
            (self.ECUADOR_BOUNDS['min_lon'], self.ECUADOR_BOUNDS['min_lat'])
        ]
        self.ecuador_polygon = Polygon(coords)
        logger.info("Polígono de límites del Ecuador creado")
    
    def is_point_in_ecuador(self, longitude, latitude):
        """
        Verifica si un punto está dentro de los límites del Ecuador.
        
        Args:
            longitude (float): Longitud del punto
            latitude (float): Latitud del punto
            
        Returns:
            bool: True si el punto está en Ecuador
        """
        point = Point(longitude, latitude)
        return self.ecuador_polygon.contains(point)
    
    def filter_elevation_data(self, elevation_data, coordinates):
        """
        Filtra datos de elevación para incluir solo puntos en Ecuador.
        
        Args:
            elevation_data (numpy.ndarray): Datos de elevación
            coordinates (tuple): Tupla con arrays de longitud y latitud
            
        Returns:
            numpy.ndarray: Datos filtrados
        """
        lon_grid, lat_grid = coordinates
        mask = np.zeros_like(elevation_data, dtype=bool)
        
        # Crear máscara para puntos dentro del Ecuador
        for i in range(elevation_data.shape[0]):
            for j in range(elevation_data.shape[1]):
                if self.is_point_in_ecuador(lon_grid[i, j], lat_grid[i, j]):
                    mask[i, j] = True
        
        # Aplicar máscara
        filtered_data = np.where(mask, elevation_data, np.nan)
        
        logger.info(f"Filtrado completado. Puntos válidos: {np.sum(mask)}")
        return filtered_data
    
    def get_ecuador_extent(self):
        """
        Retorna la extensión geográfica del Ecuador.
        
        Returns:
            dict: Diccionario con límites geográficos
        """
        return self.ECUADOR_BOUNDS.copy()
    
    def apply_elevation_range_filter(self, elevation_data, min_elevation=-500, max_elevation=7000):
        """
        Filtra elevaciones fuera del rango esperado para Ecuador.
        
        Args:
            elevation_data (numpy.ndarray): Datos de elevación
            min_elevation (float): Elevación mínima válida
            max_elevation (float): Elevación máxima válida
            
        Returns:
            numpy.ndarray: Datos filtrados
        """
        filtered_data = np.where(
            (elevation_data >= min_elevation) & (elevation_data <= max_elevation),
            elevation_data,
            np.nan
        )
        
        valid_points = np.sum(~np.isnan(filtered_data))
        total_points = elevation_data.size
        
        logger.info(f"Filtro de elevación aplicado. Puntos válidos: {valid_points}/{total_points}")
        return filtered_data
