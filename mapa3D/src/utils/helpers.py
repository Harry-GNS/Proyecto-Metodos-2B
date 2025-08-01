"""
Funciones auxiliares
===================

Este módulo contiene funciones de utilidad general
que son utilizadas en diferentes partes del proyecto.
"""

import numpy as np
import logging
import os
import time
from functools import wraps
from typing import Tuple, List, Any
import json

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_file: str = None):
    """
    Configura el sistema de logging.
    
    Args:
        level (str): Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file (str, optional): Archivo para guardar logs
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Nivel de logging inválido: {level}')
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logger.info(f"Logging configurado: nivel {level}")


def timing_decorator(func):
    """
    Decorador para medir el tiempo de ejecución de una función.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"{func.__name__} ejecutada en {execution_time:.2f} segundos")
        return result
    
    return wrapper


def validate_coordinates(longitude: float, latitude: float) -> bool:
    """
    Valida coordenadas geográficas.
    
    Args:
        longitude (float): Longitud en grados decimales
        latitude (float): Latitud en grados decimales
        
    Returns:
        bool: True si las coordenadas son válidas
    """
    return (-180 <= longitude <= 180) and (-90 <= latitude <= 90)


def degrees_to_meters(longitude: float, latitude: float) -> Tuple[float, float]:
    """
    Convierte coordenadas geográficas a metros aproximados.
    
    Args:
        longitude (float): Longitud en grados
        latitude (float): Latitud en grados
        
    Returns:
        Tuple[float, float]: Coordenadas en metros (x, y)
    """
    # Aproximación simple (válida para áreas pequeñas)
    meters_per_degree_lon = 111320 * np.cos(np.radians(latitude))
    meters_per_degree_lat = 110540
    
    x = longitude * meters_per_degree_lon
    y = latitude * meters_per_degree_lat
    
    return x, y


def calculate_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine.
    
    Args:
        lon1, lat1: Coordenadas del primer punto
        lon2, lat2: Coordenadas del segundo punto
        
    Returns:
        float: Distancia en metros
    """
    # Radio de la Tierra en metros
    R = 6371000
    
    # Convertir a radianes
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Fórmula de Haversine
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c


def create_progress_callback(total_steps: int, step_name: str = "Procesando"):
    """
    Crea una función callback para reportar progreso.
    
    Args:
        total_steps (int): Número total de pasos
        step_name (str): Nombre del proceso
        
    Returns:
        function: Función callback
    """
    def callback(current_step: int):
        percentage = (current_step / total_steps) * 100
        logger.info(f"{step_name}: {current_step}/{total_steps} ({percentage:.1f}%)")
    
    return callback


def save_metadata(data: dict, filepath: str):
    """
    Guarda metadatos en un archivo JSON.
    
    Args:
        data (dict): Diccionario con metadatos
        filepath (str): Ruta del archivo de salida
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Metadatos guardados en: {filepath}")
    except Exception as e:
        logger.error(f"Error al guardar metadatos: {e}")


def load_metadata(filepath: str) -> dict:
    """
    Carga metadatos desde un archivo JSON.
    
    Args:
        filepath (str): Ruta del archivo
        
    Returns:
        dict: Diccionario con metadatos o diccionario vacío si hay error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Metadatos cargados desde: {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error al cargar metadatos: {e}")
        return {}


def format_file_size(size_bytes: int) -> str:
    """
    Formatea un tamaño de archivo en bytes a una representación legible.
    
    Args:
        size_bytes (int): Tamaño en bytes
        
    Returns:
        str: Tamaño formateado (ej: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(np.floor(np.log(size_bytes) / np.log(1024)))
    p = np.power(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def create_bounding_box(points: np.ndarray) -> dict:
    """
    Crea una caja delimitadora para un conjunto de puntos.
    
    Args:
        points (np.ndarray): Array de puntos (N x 2 o N x 3)
        
    Returns:
        dict: Diccionario con información de la caja delimitadora
    """
    if len(points) == 0:
        return {"error": "No hay puntos"}
    
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    center = (min_coords + max_coords) / 2
    dimensions = max_coords - min_coords
    
    bbox = {
        "min": min_coords.tolist(),
        "max": max_coords.tolist(),
        "center": center.tolist(),
        "dimensions": dimensions.tolist(),
        "volume": np.prod(dimensions) if len(dimensions) == 3 else np.prod(dimensions[:2])
    }
    
    return bbox


def interpolate_missing_values(data: np.ndarray, method: str = "linear") -> np.ndarray:
    """
    Interpola valores faltantes en un array 2D.
    
    Args:
        data (np.ndarray): Array con valores faltantes (NaN)
        method (str): Método de interpolación ("linear", "nearest", "cubic")
        
    Returns:
        np.ndarray: Array con valores interpolados
    """
    from scipy.interpolate import griddata
    
    # Encontrar puntos válidos
    valid_mask = ~np.isnan(data)
    
    if not np.any(valid_mask):
        logger.warning("No hay valores válidos para interpolación")
        return data
    
    # Crear grillas de coordenadas
    rows, cols = np.mgrid[0:data.shape[0], 0:data.shape[1]]
    
    # Puntos válidos
    valid_points = np.column_stack([rows[valid_mask], cols[valid_mask]])
    valid_values = data[valid_mask]
    
    # Puntos a interpolar
    all_points = np.column_stack([rows.ravel(), cols.ravel()])
    
    # Interpolación
    try:
        interpolated_values = griddata(
            valid_points, valid_values, all_points, method=method, fill_value=np.nan
        )
        
        interpolated_data = interpolated_values.reshape(data.shape)
        
        # Combinar datos originales con interpolados
        result = np.where(valid_mask, data, interpolated_data)
        
        interpolated_count = np.sum(~valid_mask & ~np.isnan(result))
        logger.info(f"Interpolados {interpolated_count} valores usando método {method}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error en interpolación: {e}")
        return data


def memory_usage_mb() -> float:
    """
    Retorna el uso actual de memoria en MB.
    
    Returns:
        float: Uso de memoria en MB
    """
    import psutil
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def create_safe_filename(filename: str) -> str:
    """
    Crea un nombre de archivo seguro removiendo caracteres problemáticos.
    
    Args:
        filename (str): Nombre de archivo original
        
    Returns:
        str: Nombre de archivo seguro
    """
    import re
    
    # Remover caracteres problemáticos
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limitar longitud
    if len(safe_filename) > 200:
        safe_filename = safe_filename[:200]
    
    return safe_filename
