"""
Configuraciones del proyecto
===========================

Este módulo contiene todas las configuraciones y constantes
utilizadas en el proyecto.
"""

import os

# Rutas del proyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# Crear directorios si no existen
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuraciones de datos DEM
DEM_CONFIG = {
    "nodata_value": -9999,
    "valid_elevation_range": (-500, 7000),  # metros
    "default_resolution": "30m",  # resolución por defecto
    "supported_formats": [".tif", ".tiff", ".hgt"]
}

# Configuraciones del Ecuador
ECUADOR_CONFIG = {
    "bounds": {
        "min_lat": -5.0,
        "max_lat": 1.5,
        "min_lon": -81.0,
        "max_lon": -75.0
    },
    "center": {
        "lat": -1.8312,
        "lon": -78.1834
    },
    "provinces": [
        "Azuay", "Bolívar", "Cañar", "Carchi", "Chimborazo", "Cotopaxi",
        "El Oro", "Esmeraldas", "Guayas", "Imbabura", "Loja", "Los Ríos",
        "Manabí", "Morona Santiago", "Napo", "Orellana", "Pastaza",
        "Pichincha", "Santa Elena", "Santo Domingo", "Sucumbíos",
        "Tungurahua", "Zamora Chinchipe"
    ],
    "regions": {
        "Costa": {
            "provinces": ["Esmeraldas", "Manabí", "Los Ríos", "Guayas", "Santa Elena", "El Oro"],
            "bounds": {"min_lon": -81.0, "max_lon": -79.0}
        },
        "Sierra": {
            "provinces": ["Carchi", "Imbabura", "Pichincha", "Santo Domingo", "Cotopaxi", 
                         "Tungurahua", "Chimborazo", "Bolívar", "Cañar", "Azuay", "Loja"],
            "bounds": {"min_lon": -79.0, "max_lon": -77.5}
        },
        "Oriente": {
            "provinces": ["Sucumbíos", "Napo", "Orellana", "Pastaza", "Morona Santiago", 
                         "Zamora Chinchipe"],
            "bounds": {"min_lon": -77.5, "max_lon": -75.0}
        }
    }
}

# Configuraciones de malla 3D
MESH_CONFIG = {
    "default_scale_factor": 1.0,
    "default_z_scale": 1.0,
    "max_vertices": 100000,  # Límite para rendimiento
    "min_triangle_area": 1e-10,
    "smoothing": {
        "gaussian_sigma": 1.0,
        "iterations": 1
    }
}

# Configuraciones de impresión 3D
PRINTING_CONFIG = {
    "stl": {
        "binary": True,
        "precision": 6
    },
    "print_bed": {
        "max_size_mm": 200,  # mm
        "min_size_mm": 10,   # mm
        "base_thickness_mm": 2.0
    },
    "material": {
        "pla": {
            "min_wall_thickness": 0.8,  # mm
            "min_feature_size": 0.4      # mm
        }
    }
}

# Configuraciones de la interfaz
GUI_CONFIG = {
    "window": {
        "width": 1000,
        "height": 700,
        "title": "Mapa 3D del Ecuador - Generador"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(levelname)s - %(message)s"
    },
    "colors": {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "success": "#F18F01",
        "warning": "#C73E1D"
    }
}

# Configuraciones de procesamiento
PROCESSING_CONFIG = {
    "chunk_size": 1000,  # Para procesamiento por chunks
    "memory_limit_mb": 1024,  # Límite de memoria
    "parallel_processes": 4,   # Número de procesos paralelos
    "cache_enabled": True,
    "temp_dir": os.path.join(PROJECT_ROOT, "temp")
}

# Crear directorio temporal si no existe
os.makedirs(PROCESSING_CONFIG["temp_dir"], exist_ok=True)

# URLs de datos
DATA_SOURCES = {
    "srtm": {
        "url": "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/SRTM_GL1/",
        "description": "SRTM 30m resolution"
    },
    "alos": {
        "url": "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/AW3D30/",
        "description": "ALOS World 3D 30m"
    }
}

# Configuraciones de validación
VALIDATION_CONFIG = {
    "mesh": {
        "check_manifold": True,
        "check_watertight": True,
        "check_normals": True,
        "max_errors": 100
    },
    "elevation": {
        "outlier_threshold": 3.0,  # desviaciones estándar
        "interpolation_method": "linear"
    }
}
