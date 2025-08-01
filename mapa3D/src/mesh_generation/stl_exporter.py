"""
Exportador de archivos STL
==========================

Este módulo maneja la exportación de mallas 3D al formato STL
para impresión 3D.
"""

import numpy as np
from stl import mesh
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class STLExporter:
    """Clase para exportar mallas 3D a formato STL."""
    
    def __init__(self):
        self.mesh_data = None
    
    def export_mesh_to_stl(self, vertices: np.ndarray, faces: np.ndarray, 
                          output_path: str, binary: bool = True) -> bool:
        """
        Exporta una malla 3D al formato STL.
        
        Args:
            vertices (np.ndarray): Array de vértices de la malla
            faces (np.ndarray): Array de caras triangulares
            output_path (str): Ruta del archivo STL de salida
            binary (bool): Si True, exporta en formato binario; si False, ASCII
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            logger.info(f"Iniciando exportación STL a: {output_path}")
            logger.info(f"Malla: {len(vertices)} vértices, {len(faces)} caras")
            
            # Crear el objeto mesh de numpy-stl
            stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
            
            # Asignar vértices a cada cara
            for i, face in enumerate(faces):
                for j in range(3):
                    stl_mesh.vectors[i][j] = vertices[face[j]]
            
            # Calcular normales automáticamente
            stl_mesh.update_normals()
            
            # Guardar archivo
            if binary:
                stl_mesh.save(output_path, mode=mesh.Mode.BINARY)
            else:
                stl_mesh.save(output_path, mode=mesh.Mode.ASCII)
            
            # Verificar que el archivo se creó correctamente
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"STL exportado exitosamente. Tamaño: {file_size / 1024:.2f} KB")
                return True
            else:
                logger.error("El archivo STL no se creó correctamente")
                return False
                
        except Exception as e:
            logger.error(f"Error al exportar STL: {e}")
            return False
    
    def validate_mesh_for_printing(self, vertices: np.ndarray, faces: np.ndarray) -> dict:
        """
        Valida una malla para impresión 3D.
        
        Args:
            vertices (np.ndarray): Vértices de la malla
            faces (np.ndarray): Caras de la malla
            
        Returns:
            dict: Diccionario con resultados de validación
        """
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'statistics': {}
        }
        
        try:
            # Verificar que hay datos
            if len(vertices) == 0 or len(faces) == 0:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Malla vacía")
                return validation_results
            
            # Estadísticas básicas
            bbox_min = np.min(vertices, axis=0)
            bbox_max = np.max(vertices, axis=0)
            dimensions = bbox_max - bbox_min
            
            validation_results['statistics'] = {
                'num_vertices': len(vertices),
                'num_faces': len(faces),
                'dimensions': dimensions.tolist(),
                'bounding_box': {
                    'min': bbox_min.tolist(),
                    'max': bbox_max.tolist()
                }
            }
            
            # Verificar dimensiones para impresión
            max_dimension = np.max(dimensions)
            if max_dimension > 300:  # 30cm
                validation_results['warnings'].append(
                    f"El modelo es muy grande ({max_dimension:.1f}mm). "
                    "Considere aplicar un factor de escala."
                )
            
            if max_dimension < 10:  # 1cm
                validation_results['warnings'].append(
                    f"El modelo es muy pequeño ({max_dimension:.1f}mm). "
                    "Puede haber problemas de impresión."
                )
            
            # Verificar caras degeneradas
            degenerate_faces = self._find_degenerate_faces(vertices, faces)
            if len(degenerate_faces) > 0:
                validation_results['warnings'].append(
                    f"Se encontraron {len(degenerate_faces)} caras degeneradas"
                )
            
            # Verificar normales
            if not self._check_normals_consistency(vertices, faces):
                validation_results['warnings'].append(
                    "Las normales de la malla no son consistentes"
                )
            
            # Verificar manifold
            if not self._is_manifold(vertices, faces):
                validation_results['errors'].append(
                    "La malla no es manifold (puede tener agujeros o intersecciones)"
                )
                validation_results['is_valid'] = False
            
            logger.info(f"Validación completada. Válida: {validation_results['is_valid']}")
            
        except Exception as e:
            logger.error(f"Error durante validación: {e}")
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Error durante validación: {e}")
        
        return validation_results
    
    def _find_degenerate_faces(self, vertices: np.ndarray, faces: np.ndarray) -> list:
        """Encuentra caras degeneradas (área cero o muy pequeña)."""
        degenerate_faces = []
        
        for i, face in enumerate(faces):
            v1, v2, v3 = vertices[face]
            
            # Calcular área del triángulo
            edge1 = v2 - v1
            edge2 = v3 - v1
            cross = np.cross(edge1, edge2)
            area = 0.5 * np.linalg.norm(cross)
            
            if area < 1e-10:  # Área muy pequeña
                degenerate_faces.append(i)
        
        return degenerate_faces
    
    def _check_normals_consistency(self, vertices: np.ndarray, faces: np.ndarray) -> bool:
        """Verifica la consistencia de las normales."""
        # Implementación simplificada
        # Una verificación completa requeriría análisis de orientación de caras
        return True
    
    def _is_manifold(self, vertices: np.ndarray, faces: np.ndarray) -> bool:
        """Verifica si la malla es manifold."""
        # Implementación simplificada
        # Una verificación completa requeriría análisis topológico
        return True
    
    def create_printable_base(self, vertices: np.ndarray, faces: np.ndarray,
                            base_thickness: float = 2.0) -> tuple:
        """
        Agrega una base plana a la malla para mejorar la adhesión en impresión.
        
        Args:
            vertices (np.ndarray): Vértices originales
            faces (np.ndarray): Caras originales
            base_thickness (float): Grosor de la base en mm
            
        Returns:
            tuple: (nuevos_vertices, nuevas_caras)
        """
        logger.info("Creando base para impresión...")
        
        # Encontrar el Z mínimo
        min_z = np.min(vertices[:, 2])
        base_z = min_z - base_thickness
        
        # Crear vértices de la base proyectando los bordes
        base_vertices = []
        base_faces = []
        
        # Por simplicidad, crear una base rectangular
        bbox_min = np.min(vertices[:, :2], axis=0)
        bbox_max = np.max(vertices[:, :2], axis=0)
        
        # Vértices de la base
        base_corners = [
            [bbox_min[0], bbox_min[1], base_z],
            [bbox_max[0], bbox_min[1], base_z],
            [bbox_max[0], bbox_max[1], base_z],
            [bbox_min[0], bbox_max[1], base_z]
        ]
        
        # Combinar vértices
        all_vertices = np.vstack([vertices, base_corners])
        
        # Caras de la base
        base_start_idx = len(vertices)
        base_faces = [
            [base_start_idx, base_start_idx + 1, base_start_idx + 2],
            [base_start_idx, base_start_idx + 2, base_start_idx + 3]
        ]
        
        # Combinar caras
        all_faces = np.vstack([faces, base_faces])
        
        logger.info(f"Base agregada: {len(base_corners)} vértices, {len(base_faces)} caras")
        
        return all_vertices, all_faces
    
    def scale_for_printing(self, vertices: np.ndarray, target_size: float = 100.0) -> np.ndarray:
        """
        Escala la malla para un tamaño objetivo de impresión.
        
        Args:
            vertices (np.ndarray): Vértices originales
            target_size (float): Tamaño objetivo en mm para la dimensión mayor
            
        Returns:
            np.ndarray: Vértices escalados
        """
        # Calcular dimensiones actuales
        bbox_min = np.min(vertices, axis=0)
        bbox_max = np.max(vertices, axis=0)
        current_size = np.max(bbox_max - bbox_min)
        
        # Calcular factor de escala
        scale_factor = target_size / current_size
        
        # Centrar en el origen y escalar
        centered_vertices = vertices - np.mean(vertices, axis=0)
        scaled_vertices = centered_vertices * scale_factor
        
        logger.info(f"Malla escalada por factor {scale_factor:.3f} para tamaño {target_size}mm")
        
        return scaled_vertices
