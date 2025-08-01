"""
Pruebas unitarias para el módulo de procesamiento de datos
========================================================

Este módulo contiene pruebas unitarias para validar el funcionamiento
de los componentes de procesamiento de datos DEM.
"""

import unittest
import numpy as np
import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_processing.dem_loader import DEMLoader
from data_processing.ecuador_filter import EcuadorFilter
from data_processing.political_segmentation import PoliticalSegmentation


class TestDEMLoader(unittest.TestCase):
    """Pruebas para la clase DEMLoader."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.dem_loader = DEMLoader()
    
    def test_initialization(self):
        """Prueba la inicialización del DEMLoader."""
        self.assertIsNone(self.dem_loader.dem_data)
        self.assertIsNone(self.dem_loader.transform)
        self.assertIsNone(self.dem_loader.crs)
        self.assertIsNone(self.dem_loader.bounds)
    
    def test_apply_nodata_mask(self):
        """Prueba la aplicación de máscara NoData."""
        # Crear datos de prueba
        test_data = np.array([[1, 2, -9999], [4, -9999, 6]])
        self.dem_loader.dem_data = test_data.copy()
        
        # Aplicar máscara
        self.dem_loader.apply_nodata_mask(-9999)
        
        # Verificar que los valores NoData se convirtieron a NaN
        self.assertTrue(np.isnan(self.dem_loader.dem_data[0, 2]))
        self.assertTrue(np.isnan(self.dem_loader.dem_data[1, 1]))
        self.assertEqual(self.dem_loader.dem_data[0, 0], 1)
        self.assertEqual(self.dem_loader.dem_data[1, 2], 6)
    
    def test_get_metadata_without_data(self):
        """Prueba obtener metadatos sin datos cargados."""
        metadata = self.dem_loader.get_metadata()
        self.assertIsNone(metadata)


class TestEcuadorFilter(unittest.TestCase):
    """Pruebas para la clase EcuadorFilter."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.ecuador_filter = EcuadorFilter()
    
    def test_initialization(self):
        """Prueba la inicialización del filtro."""
        self.assertIsNotNone(self.ecuador_filter.ecuador_polygon)
        
        # Verificar límites del Ecuador
        bounds = self.ecuador_filter.ECUADOR_BOUNDS
        self.assertEqual(bounds['min_lat'], -5.0)
        self.assertEqual(bounds['max_lat'], 1.5)
        self.assertEqual(bounds['min_lon'], -81.0)
        self.assertEqual(bounds['max_lon'], -75.0)
    
    def test_point_in_ecuador(self):
        """Prueba la verificación de puntos dentro del Ecuador."""
        # Punto dentro del Ecuador (Quito aproximadamente)
        self.assertTrue(self.ecuador_filter.is_point_in_ecuador(-78.5, -0.2))
        
        # Punto fuera del Ecuador
        self.assertFalse(self.ecuador_filter.is_point_in_ecuador(-70.0, 10.0))
    
    def test_get_ecuador_extent(self):
        """Prueba obtener la extensión del Ecuador."""
        extent = self.ecuador_filter.get_ecuador_extent()
        
        self.assertIn('min_lat', extent)
        self.assertIn('max_lat', extent)
        self.assertIn('min_lon', extent)
        self.assertIn('max_lon', extent)
    
    def test_elevation_range_filter(self):
        """Prueba el filtro de rango de elevación."""
        # Datos de prueba con elevaciones fuera de rango
        test_data = np.array([[100, -1000, 5000], [8000, 3000, 200]])
        
        filtered_data = self.ecuador_filter.apply_elevation_range_filter(
            test_data, min_elevation=-500, max_elevation=7000
        )
        
        # Verificar que valores fuera de rango se convirtieron a NaN
        self.assertTrue(np.isnan(filtered_data[0, 1]))  # -1000 < -500
        self.assertTrue(np.isnan(filtered_data[1, 0]))  # 8000 > 7000
        
        # Verificar que valores dentro del rango se mantuvieron
        self.assertEqual(filtered_data[0, 0], 100)
        self.assertEqual(filtered_data[1, 1], 3000)


class TestPoliticalSegmentation(unittest.TestCase):
    """Pruebas para la clase PoliticalSegmentation."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.political_seg = PoliticalSegmentation()
    
    def test_initialization(self):
        """Prueba la inicialización de la segmentación política."""
        self.assertIsInstance(self.political_seg.continental_provinces, dict)
        
        # Verificar que Galápagos no está incluida
        provinces = self.political_seg.get_province_list()
        self.assertNotIn('Galápagos', provinces)
        self.assertIn('Pichincha', provinces)
        self.assertIn('Guayas', provinces)
    
    def test_get_province_center(self):
        """Prueba obtener el centro de una provincia."""
        # Provincia existente
        center = self.political_seg.get_province_center('Pichincha')
        self.assertIsNotNone(center)
        self.assertEqual(len(center), 2)  # longitud, latitud
        
        # Provincia no existente
        center = self.political_seg.get_province_center('ProvinciasInexistente')
        self.assertIsNone(center)
    
    def test_segment_by_coordinates(self):
        """Prueba la segmentación por coordenadas."""
        # Crear datos de prueba
        lons = np.array([[-80.0, -78.0], [-76.0, -78.0]])
        lats = np.array([[-1.0, -1.0], [-1.0, -1.0]])
        elevations = np.array([[100, 200], [300, 400]])
        
        segments = self.political_seg.segment_by_coordinates(
            elevations, (lons, lats)
        )
        
        # Verificar que se crearon las regiones esperadas
        self.assertIn('Costa', segments)
        self.assertIn('Sierra', segments)
        self.assertIn('Oriente', segments)
        
        # Verificar estructura de cada segmento
        for region_name, segment in segments.items():
            self.assertIn('data', segment)
            self.assertIn('mask', segment)
            self.assertIn('bounds', segment)
            self.assertIn('valid_points', segment)


if __name__ == '__main__':
    # Configurar logging para las pruebas
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar todas las pruebas
    unittest.main(verbosity=2)
