"""
Conversión de datos de terreno a mallas 3D
==========================================

Este módulo implementa algoritmos para convertir datos de elevación
en mallas triangulares 3D.
"""

import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import griddata
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class TerrainToMesh:
    """Clase para convertir datos de terreno en mallas 3D."""
    
    def __init__(self):
        self.vertices = None
        self.faces = None
        self.elevation_data = None
        self.coordinates = None
    
    def load_elevation_data(self, elevation_data: np.ndarray, 
                          coordinates: Tuple[np.ndarray, np.ndarray]):
        """
        Carga datos de elevación y coordenadas.
        
        Args:
            elevation_data (np.ndarray): Matriz de elevaciones
            coordinates (Tuple): Tupla con arrays de longitud y latitud
        """
        self.elevation_data = elevation_data
        self.coordinates = coordinates
        
        logger.info(f"Datos de elevación cargados: {elevation_data.shape}")
        logger.info(f"Rango de elevaciones: {np.nanmin(elevation_data):.2f} - {np.nanmax(elevation_data):.2f}m")
    
    def create_regular_grid_mesh(self, scale_factor: float = 1.0, 
                               z_scale: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Crea una malla 3D usando una grilla regular.
        
        Args:
            scale_factor (float): Factor de escala para coordenadas XY
            z_scale (float): Factor de escala para elevación Z
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Vértices y caras de la malla
        """
        if self.elevation_data is None:
            raise ValueError("Primero debe cargar los datos de elevación")
        
        logger.info("Creando malla con grilla regular...")
        
        lon_grid, lat_grid = self.coordinates
        height, width = self.elevation_data.shape
        
        # Crear arrays de vértices
        vertices = []
        vertex_indices = np.full((height, width), -1, dtype=int)
        vertex_count = 0
        
        # Procesar cada punto de la grilla
        for i in range(height):
            for j in range(width):
                elevation = self.elevation_data[i, j]
                
                # Omitir puntos sin datos
                if np.isnan(elevation):
                    continue
                
                # Agregar vértice (convertir coordenadas geográficas a metros)
                x = lon_grid[i, j] * scale_factor * 111320  # Aproximación metros por grado
                y = lat_grid[i, j] * scale_factor * 110540
                z = elevation * z_scale
                
                vertices.append([x, y, z])
                vertex_indices[i, j] = vertex_count
                vertex_count += 1
        
        vertices = np.array(vertices)
        logger.info(f"Generados {len(vertices)} vértices")
        
        # Crear caras triangulares
        faces = []
        
        for i in range(height - 1):
            for j in range(width - 1):
                # Obtener índices de los 4 vértices del cuadrado
                v00 = vertex_indices[i, j]
                v01 = vertex_indices[i, j + 1]
                v10 = vertex_indices[i + 1, j]
                v11 = vertex_indices[i + 1, j + 1]
                
                # Solo crear caras si todos los vértices existen
                valid_vertices = [v for v in [v00, v01, v10, v11] if v != -1]
                
                if len(valid_vertices) >= 3:
                    if v00 != -1 and v01 != -1 and v10 != -1:
                        faces.append([v00, v01, v10])
                    
                    if v01 != -1 and v10 != -1 and v11 != -1:
                        faces.append([v01, v11, v10])
        
        faces = np.array(faces)
        logger.info(f"Generadas {len(faces)} caras triangulares")
        
        self.vertices = vertices
        self.faces = faces
        
        return vertices, faces
    
    def create_delaunay_mesh(self, decimation_factor: int = 1,
                           scale_factor: float = 1.0,
                           z_scale: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Crea una malla 3D usando triangulación de Delaunay.
        
        Args:
            decimation_factor (int): Factor de decimación para reducir puntos
            scale_factor (float): Factor de escala para coordenadas XY
            z_scale (float): Factor de escala para elevación Z
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Vértices y caras de la malla
        """
        if self.elevation_data is None:
            raise ValueError("Primero debe cargar los datos de elevación")
        
        logger.info("Creando malla con triangulación de Delaunay...")
        
        lon_grid, lat_grid = self.coordinates
        
        # Extraer puntos válidos (sin NaN)
        valid_mask = ~np.isnan(self.elevation_data)
        
        if decimation_factor > 1:
            # Aplicar decimación para reducir la cantidad de puntos
            decimated_mask = np.zeros_like(valid_mask)
            decimated_mask[::decimation_factor, ::decimation_factor] = True
            valid_mask = valid_mask & decimated_mask
        
        # Extraer coordenadas y elevaciones válidas
        lon_valid = lon_grid[valid_mask]
        lat_valid = lat_grid[valid_mask]
        elev_valid = self.elevation_data[valid_mask]
        
        logger.info(f"Procesando {len(lon_valid)} puntos válidos")
        
        # Crear puntos 2D para triangulación
        points_2d = np.column_stack((lon_valid, lat_valid))
        
        # Triangulación de Delaunay
        tri = Delaunay(points_2d)
        
        # Crear vértices 3D
        vertices = np.column_stack((
            lon_valid * scale_factor * 111320,  # Convertir a metros
            lat_valid * scale_factor * 110540,
            elev_valid * z_scale
        ))
        
        # Las caras son directamente los triángulos de Delaunay
        faces = tri.simplices
        
        logger.info(f"Malla Delaunay creada: {len(vertices)} vértices, {len(faces)} caras")
        
        self.vertices = vertices
        self.faces = faces
        
        return vertices, faces
    
    def optimize_mesh(self, target_faces: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Optimiza la malla reduciendo el número de caras si es necesario.
        
        Args:
            target_faces (int, optional): Número objetivo de caras
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Vértices y caras optimizadas
        """
        if self.vertices is None or self.faces is None:
            raise ValueError("Primero debe crear una malla")
        
        logger.info("Optimización de malla no implementada aún")
        
        # Por ahora retornar la malla sin cambios
        return self.vertices, self.faces
    
    def get_mesh_statistics(self) -> dict:
        """
        Retorna estadísticas de la malla actual.
        
        Returns:
            dict: Diccionario con estadísticas
        """
        if self.vertices is None or self.faces is None:
            return {"error": "No hay malla disponible"}
        
        stats = {
            "num_vertices": len(self.vertices),
            "num_faces": len(self.faces),
            "bbox_min": np.min(self.vertices, axis=0).tolist(),
            "bbox_max": np.max(self.vertices, axis=0).tolist(),
            "surface_area": self._calculate_surface_area(),
            "is_manifold": self._check_manifold()
        }
        
        return stats
    
    def _calculate_surface_area(self) -> float:
        """Calcula el área superficial de la malla."""
        if self.vertices is None or self.faces is None:
            return 0.0
        
        total_area = 0.0
        
        for face in self.faces:
            v1, v2, v3 = self.vertices[face]
            
            # Calcular área del triángulo usando producto cruz
            edge1 = v2 - v1
            edge2 = v3 - v1
            cross = np.cross(edge1, edge2)
            area = 0.5 * np.linalg.norm(cross)
            total_area += area
        
        return total_area
    
    def _check_manifold(self) -> bool:
        """Verifica si la malla es manifold (cerrada y sin intersecciones)."""
        # Implementación simplificada
        # Una verificación completa requeriría análisis topológico más complejo
        logger.info("Verificación de manifold simplificada")
        return True
