"""
Cargador avanzado de datos DEM
=============================

Este módulo maneja la carga de archivos DEM reales desde diferentes fuentes
y formatos, incluyendo datos de la carpeta local.
"""

import os
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
import glob

logger = logging.getLogger(__name__)


class AdvancedDEMLoader:
    """Cargador avanzado de archivos DEM con soporte para múltiples formatos."""
    
    def __init__(self, data_directory: str = None):
        """
        Inicializa el cargador de DEM.
        
        Args:
            data_directory: Directorio base donde buscar archivos DEM
        """
        self.data_directory = data_directory or self._get_default_data_dir()
        self.dem_data = None
        self.metadata = {}
        self.coordinate_system = None
        
        # Formatos soportados
        self.supported_formats = {
            '.tif': 'GeoTIFF',
            '.tiff': 'GeoTIFF', 
            '.hgt': 'SRTM Height',
            '.img': 'ERDAS Imagine',
            '.bil': 'Band Interleaved by Line',
            '.asc': 'ASCII Grid',
            '.xyz': 'XYZ Point Cloud'
        }
        
        logger.info(f"DEM Loader inicializado. Directorio de datos: {self.data_directory}")
    
    def _get_default_data_dir(self) -> str:
        """Obtiene el directorio de datos por defecto."""
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(current_dir, "data", "raw")
    
    def scan_available_files(self) -> Dict[str, List[str]]:
        """
        Escanea todos los archivos DEM disponibles en el directorio.
        
        Returns:
            Dict: Diccionario con archivos organizados por formato
        """
        available_files = {}
        
        for ext, format_name in self.supported_formats.items():
            pattern = os.path.join(self.data_directory, "**", f"*{ext}")
            files = glob.glob(pattern, recursive=True)
            
            if files:
                available_files[format_name] = []
                for file in files:
                    file_info = {
                        'path': file,
                        'name': os.path.basename(file),
                        'size': self._get_file_size(file),
                        'relative_path': os.path.relpath(file, self.data_directory)
                    }
                    available_files[format_name].append(file_info)
        
        logger.info(f"Archivos encontrados: {sum(len(files) for files in available_files.values())}")
        return available_files
    
    def _get_file_size(self, filepath: str) -> str:
        """Obtiene el tamaño de un archivo en formato legible."""
        try:
            size_bytes = os.path.getsize(filepath)
            
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024**2:
                return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                return f"{size_bytes/(1024**2):.1f} MB"
            else:
                return f"{size_bytes/(1024**3):.1f} GB"
        except OSError:
            return "Desconocido"
    
    def load_dem_file(self, filepath: str, zone_bounds: Dict = None) -> bool:
        """
        Carga un archivo DEM específico.
        
        Args:
            filepath: Ruta al archivo DEM
            zone_bounds: Límites geográficos para recortar (opcional)
            
        Returns:
            bool: True si la carga fue exitosa
        """
        if not os.path.exists(filepath):
            logger.error(f"Archivo no encontrado: {filepath}")
            return False
        
        file_ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if file_ext in ['.tif', '.tiff']:
                return self._load_geotiff(filepath, zone_bounds)
            elif file_ext == '.hgt':
                return self._load_hgt(filepath, zone_bounds)
            elif file_ext == '.asc':
                return self._load_ascii_grid(filepath, zone_bounds)
            elif file_ext == '.xyz':
                return self._load_xyz(filepath, zone_bounds)
            else:
                # Intentar como archivo de texto genérico
                return self._load_generic_text(filepath, zone_bounds)
                
        except Exception as e:
            logger.error(f"Error al cargar archivo {filepath}: {e}")
            return False
    
    def _load_geotiff(self, filepath: str, zone_bounds: Dict = None) -> bool:
        """Carga archivo GeoTIFF usando rasterio si está disponible."""
        try:
            import rasterio
            from rasterio.mask import mask
            from shapely.geometry import box
            
            with rasterio.open(filepath) as src:
                # Obtener metadatos
                self.metadata = {
                    'width': src.width,
                    'height': src.height,
                    'count': src.count,
                    'dtype': src.dtypes[0],
                    'crs': src.crs,
                    'transform': src.transform,
                    'bounds': src.bounds
                }
                
                if zone_bounds:
                    # Recortar por zona específica
                    geom = [box(zone_bounds['min_lon'], zone_bounds['min_lat'],
                               zone_bounds['max_lon'], zone_bounds['max_lat'])]
                    
                    out_image, out_transform = mask(src, geom, crop=True)
                    self.dem_data = out_image[0]  # Primera banda
                    self.metadata['transform'] = out_transform
                else:
                    # Leer todo el archivo
                    self.dem_data = src.read(1)
                
                # Manejar valores NoData
                if src.nodata is not None:
                    self.dem_data = np.where(self.dem_data == src.nodata, np.nan, self.dem_data)
                
                logger.info(f"GeoTIFF cargado: {filepath}")
                logger.info(f"Dimensiones: {self.dem_data.shape}")
                logger.info(f"Rango elevación: {np.nanmin(self.dem_data):.1f} - {np.nanmax(self.dem_data):.1f}m")
                
                return True
                
        except ImportError:
            logger.warning("rasterio no disponible, intentando método alternativo")
            return self._load_tiff_alternative(filepath, zone_bounds)
        except Exception as e:
            logger.error(f"Error cargando GeoTIFF: {e}")
            return False
    
    def _load_tiff_alternative(self, filepath: str, zone_bounds: Dict = None) -> bool:
        """Método alternativo para cargar TIFF sin rasterio."""
        try:
            from PIL import Image
            import numpy as np
            
            # Cargar imagen
            img = Image.open(filepath)
            self.dem_data = np.array(img)
            
            # Metadatos básicos
            self.metadata = {
                'width': img.width,
                'height': img.height,
                'mode': img.mode
            }
            
            # Si es una imagen en escala de grises, tratar como elevación
            if len(self.dem_data.shape) == 2:
                # Normalizar a rango de elevación típico (0-4000m)
                self.dem_data = (self.dem_data / 255.0) * 4000
                
                logger.info(f"TIFF alternativo cargado: {filepath}")
                logger.info(f"Dimensiones: {self.dem_data.shape}")
                return True
            else:
                logger.error("Formato TIFF no soportado (debe ser escala de grises)")
                return False
                
        except ImportError:
            logger.error("PIL no disponible para cargar TIFF")
            return False
        except Exception as e:
            logger.error(f"Error en método alternativo TIFF: {e}")
            return False
    
    def _load_hgt(self, filepath: str, zone_bounds: Dict = None) -> bool:
        """Carga archivo SRTM HGT."""
        try:
            # Los archivos .hgt son arrays binarios de 16-bit signed integers
            # Usualmente 1201x1201 o 3601x3601 puntos
            
            file_size = os.path.getsize(filepath)
            
            # Determinar dimensiones basado en el tamaño del archivo
            if file_size == 1201 * 1201 * 2:  # SRTM-3 (3 arc-second)
                size = 1201
            elif file_size == 3601 * 3601 * 2:  # SRTM-1 (1 arc-second)
                size = 3601
            else:
                logger.error(f"Tamaño de archivo HGT no estándar: {file_size}")
                return False
            
            # Leer archivo binario
            with open(filepath, 'rb') as f:
                # Big-endian signed 16-bit integers
                data = np.frombuffer(f.read(), np.dtype('>i2'))
                self.dem_data = data.reshape((size, size)).astype(np.float32)
            
            # Valores -32768 son NoData
            self.dem_data = np.where(self.dem_data == -32768, np.nan, self.dem_data)
            
            # Metadatos básicos
            self.metadata = {
                'width': size,
                'height': size,
                'format': 'SRTM HGT',
                'resolution': '3 arc-second' if size == 1201 else '1 arc-second'
            }
            
            logger.info(f"Archivo HGT cargado: {filepath}")
            logger.info(f"Dimensiones: {self.dem_data.shape}")
            logger.info(f"Rango elevación: {np.nanmin(self.dem_data):.1f} - {np.nanmax(self.dem_data):.1f}m")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cargando archivo HGT: {e}")
            return False
    
    def _load_ascii_grid(self, filepath: str, zone_bounds: Dict = None) -> bool:
        """Carga archivo ASCII Grid (.asc)."""
        try:
            with open(filepath, 'r') as f:
                # Leer header
                header = {}
                for i in range(6):  # Header típico tiene 6 líneas
                    line = f.readline().strip().split()
                    if len(line) == 2:
                        header[line[0].lower()] = float(line[1]) if '.' in line[1] else int(line[1])
                
                # Leer datos
                data_lines = f.readlines()
                
            # Parsear datos
            data = []
            for line in data_lines:
                if line.strip():
                    row = [float(x) if x != str(header.get('nodata_value', -9999)) else np.nan 
                           for x in line.strip().split()]
                    data.append(row)
            
            self.dem_data = np.array(data)
            
            # Guardar metadatos
            self.metadata = header
            self.metadata['format'] = 'ASCII Grid'
            
            logger.info(f"ASCII Grid cargado: {filepath}")
            logger.info(f"Dimensiones: {self.dem_data.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cargando ASCII Grid: {e}")
            return False
    
    def _load_xyz(self, filepath: str, zone_bounds: Dict = None) -> bool:
        """Carga archivo XYZ (punto cloud)."""
        try:
            # Leer archivo XYZ
            data = np.loadtxt(filepath)
            
            if data.shape[1] < 3:
                logger.error("Archivo XYZ debe tener al menos 3 columnas (X, Y, Z)")
                return False
            
            x_coords = data[:, 0]
            y_coords = data[:, 1]
            z_values = data[:, 2]
            
            # Crear grilla regular
            x_unique = np.unique(x_coords)
            y_unique = np.unique(y_coords)
            
            # Interpolar a grilla regular
            from scipy.interpolate import griddata
            
            xi, yi = np.meshgrid(x_unique, y_unique)
            self.dem_data = griddata((x_coords, y_coords), z_values, (xi, yi), method='linear')
            
            self.metadata = {
                'format': 'XYZ Point Cloud',
                'original_points': len(data),
                'gridded_size': self.dem_data.shape,
                'x_range': (np.min(x_coords), np.max(x_coords)),
                'y_range': (np.min(y_coords), np.max(y_coords))
            }
            
            logger.info(f"Archivo XYZ cargado: {filepath}")
            logger.info(f"Puntos originales: {len(data)}, Grilla: {self.dem_data.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cargando archivo XYZ: {e}")
            return False
    
    def _load_generic_text(self, filepath: str, zone_bounds: Dict = None) -> bool:
        """Intenta cargar como archivo de texto genérico."""
        try:
            # Intentar diferentes delimitadores
            for delimiter in [' ', '\t', ',', ';']:
                try:
                    data = np.loadtxt(filepath, delimiter=delimiter)
                    
                    if len(data.shape) == 2 and data.shape[0] > 10 and data.shape[1] > 10:
                        self.dem_data = data
                        
                        self.metadata = {
                            'format': 'Generic Text',
                            'delimiter': delimiter,
                            'shape': data.shape
                        }
                        
                        logger.info(f"Archivo de texto genérico cargado: {filepath}")
                        logger.info(f"Dimensiones: {self.dem_data.shape}")
                        return True
                        
                except:
                    continue
            
            logger.error("No se pudo interpretar el archivo como DEM")
            return False
            
        except Exception as e:
            logger.error(f"Error cargando archivo genérico: {e}")
            return False
    
    def get_elevation_data(self) -> np.ndarray:
        """Retorna los datos de elevación cargados."""
        return self.dem_data
    
    def get_metadata(self) -> Dict:
        """Retorna metadatos del archivo cargado."""
        return self.metadata
    
    def create_sample_data_file(self, output_path: str, zone_bounds: Dict = None):
        """
        Crea un archivo de datos de muestra para pruebas.
        
        Args:
            output_path: Ruta donde guardar el archivo
            zone_bounds: Límites de la zona (opcional)
        """
        try:
            if zone_bounds:
                min_lat, max_lat = zone_bounds['min_lat'], zone_bounds['max_lat']
                min_lon, max_lon = zone_bounds['min_lon'], zone_bounds['max_lon']
            else:
                # Ecuador por defecto
                min_lat, max_lat = -5.0, 1.5
                min_lon, max_lon = -81.0, -75.0
            
            # Crear grilla de coordenadas
            lats = np.linspace(min_lat, max_lat, 100)
            lons = np.linspace(min_lon, max_lon, 100)
            
            lat_grid, lon_grid = np.meshgrid(lats, lons)
            
            # Generar elevaciones sintéticas realistas
            # Modelo topográfico simple basado en distancia a la costa y latitud
            elevation = (
                1000 +  # Elevación base
                2000 * np.abs(lon_grid + 78) +  # Aumenta hacia el este (Andes)
                500 * np.sin(lat_grid * 2) +  # Variación por latitud
                200 * np.random.random(lat_grid.shape)  # Ruido realista
            )
            
            # Asegurar valores realistas para Ecuador
            elevation = np.clip(elevation, 0, 6000)
            
            # Guardar como archivo ASCII
            header = f"""ncols {elevation.shape[1]}
nrows {elevation.shape[0]}
xllcorner {min_lon}
yllcorner {min_lat}
cellsize {(max_lon - min_lon) / elevation.shape[1]:.6f}
NODATA_value -9999
"""
            
            with open(output_path, 'w') as f:
                f.write(header)
                np.savetxt(f, elevation, fmt='%.1f')
            
            logger.info(f"Archivo de muestra creado: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creando archivo de muestra: {e}")
