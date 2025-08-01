"""
Segmentación política del territorio ecuatoriano
==============================================

Este módulo maneja la segmentación del territorio ecuatoriano por
divisiones políticas (provincias, cantones, etc.).
"""

import numpy as np
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class PoliticalSegmentation:
    """Clase para manejar divisiones políticas del Ecuador."""
    
    # Provincias del Ecuador con coordenadas aproximadas
    PROVINCES = {
        'Azuay': {'center': (-78.9, -2.9), 'code': 'AZ'},
        'Bolívar': {'center': (-79.0, -1.6), 'code': 'BO'},
        'Cañar': {'center': (-78.9, -2.5), 'code': 'CA'},
        'Carchi': {'center': (-78.1, 0.7), 'code': 'CR'},
        'Chimborazo': {'center': (-78.7, -1.7), 'code': 'CH'},
        'Cotopaxi': {'center': (-78.6, -0.9), 'code': 'CO'},
        'El Oro': {'center': (-79.7, -3.3), 'code': 'EO'},
        'Esmeraldas': {'center': (-79.4, 0.9), 'code': 'ES'},
        'Galápagos': {'center': (-90.4, -0.7), 'code': 'GA'},  # Excluida del continental
        'Guayas': {'center': (-79.9, -2.2), 'code': 'GU'},
        'Imbabura': {'center': (-78.1, 0.3), 'code': 'IM'},
        'Loja': {'center': (-79.2, -4.0), 'code': 'LO'},
        'Los Ríos': {'center': (-79.5, -1.8), 'code': 'LR'},
        'Manabí': {'center': (-80.4, -1.0), 'code': 'MA'},
        'Morona Santiago': {'center': (-78.1, -2.3), 'code': 'MS'},
        'Napo': {'center': (-77.8, -1.0), 'code': 'NA'},
        'Orellana': {'center': (-76.6, -0.5), 'code': 'OR'},
        'Pastaza': {'center': (-76.6, -1.5), 'code': 'PA'},
        'Pichincha': {'center': (-78.5, -0.2), 'code': 'PI'},
        'Santa Elena': {'center': (-80.9, -2.2), 'code': 'SE'},
        'Santo Domingo': {'center': (-79.2, -0.4), 'code': 'SD'},
        'Sucumbíos': {'center': (-76.6, 0.1), 'code': 'SU'},
        'Tungurahua': {'center': (-78.6, -1.2), 'code': 'TU'},
        'Zamora Chinchipe': {'center': (-78.9, -4.1), 'code': 'ZC'}
    }
    
    def __init__(self):
        self.continental_provinces = self._get_continental_provinces()
        logger.info(f"Segmentación política inicializada con {len(self.continental_provinces)} provincias continentales")
    
    def _get_continental_provinces(self) -> Dict:
        """Retorna solo las provincias continentales (excluyendo Galápagos)."""
        return {k: v for k, v in self.PROVINCES.items() if k != 'Galápagos'}
    
    def get_province_list(self) -> List[str]:
        """
        Retorna la lista de nombres de provincias continentales.
        
        Returns:
            List[str]: Lista de nombres de provincias
        """
        return list(self.continental_provinces.keys())
    
    def get_province_center(self, province_name: str) -> Tuple[float, float]:
        """
        Retorna las coordenadas del centro aproximado de una provincia.
        
        Args:
            province_name (str): Nombre de la provincia
            
        Returns:
            Tuple[float, float]: (longitud, latitud) del centro
        """
        if province_name in self.continental_provinces:
            return self.continental_provinces[province_name]['center']
        else:
            logger.warning(f"Provincia no encontrada: {province_name}")
            return None
    
    def segment_by_coordinates(self, elevation_data: np.ndarray, 
                             coordinates: Tuple[np.ndarray, np.ndarray]) -> Dict:
        """
        Segmenta los datos de elevación por regiones aproximadas.
        
        Args:
            elevation_data (np.ndarray): Datos de elevación
            coordinates (Tuple): Arrays de longitud y latitud
            
        Returns:
            Dict: Diccionario con segmentos por región
        """
        lon_grid, lat_grid = coordinates
        segments = {}
        
        # Definir regiones generales
        regions = {
            'Costa': {'lon_range': (-81.0, -79.0), 'lat_range': (-5.0, 1.5)},
            'Sierra': {'lon_range': (-79.0, -77.5), 'lat_range': (-5.0, 1.5)},
            'Oriente': {'lon_range': (-77.5, -75.0), 'lat_range': (-5.0, 1.5)}
        }
        
        for region_name, bounds in regions.items():
            lon_min, lon_max = bounds['lon_range']
            lat_min, lat_max = bounds['lat_range']
            
            mask = ((lon_grid >= lon_min) & (lon_grid <= lon_max) & 
                   (lat_grid >= lat_min) & (lat_grid <= lat_max))
            
            regional_data = np.where(mask, elevation_data, np.nan)
            segments[region_name] = {
                'data': regional_data,
                'mask': mask,
                'bounds': bounds,
                'valid_points': np.sum(~np.isnan(regional_data))
            }
            
            logger.info(f"Región {region_name}: {segments[region_name]['valid_points']} puntos válidos")
        
        return segments
    
    def get_region_statistics(self, segmented_data: Dict) -> Dict:
        """
        Calcula estadísticas para cada región segmentada.
        
        Args:
            segmented_data (Dict): Datos segmentados por región
            
        Returns:
            Dict: Estadísticas por región
        """
        statistics = {}
        
        for region_name, region_data in segmented_data.items():
            data = region_data['data']
            valid_data = data[~np.isnan(data)]
            
            if len(valid_data) > 0:
                statistics[region_name] = {
                    'min_elevation': np.min(valid_data),
                    'max_elevation': np.max(valid_data),
                    'mean_elevation': np.mean(valid_data),
                    'std_elevation': np.std(valid_data),
                    'valid_points': len(valid_data)
                }
            else:
                statistics[region_name] = {
                    'min_elevation': np.nan,
                    'max_elevation': np.nan,
                    'mean_elevation': np.nan,
                    'std_elevation': np.nan,
                    'valid_points': 0
                }
        
        return statistics
