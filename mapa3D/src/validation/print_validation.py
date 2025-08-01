"""
Validación para impresión 3D
============================

Este módulo implementa validaciones específicas para asegurar
que los modelos 3D sean apropiados para impresión.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class PrintValidation:
    """Clase para validar modelos 3D para impresión."""
    
    def __init__(self):
        # Configuración por defecto para impresión 3D
        self.config = {
            'min_wall_thickness': 0.8,      # mm
            'min_feature_size': 0.4,        # mm
            'max_overhang_angle': 45,       # grados
            'max_print_size': 200,          # mm
            'min_print_size': 5,            # mm
            'layer_height': 0.2,            # mm
            'nozzle_diameter': 0.4          # mm
        }
    
    def validate_for_printing(self, vertices: np.ndarray, faces: np.ndarray) -> Dict:
        """
        Realiza una validación completa para impresión 3D.
        
        Args:
            vertices (np.ndarray): Vértices de la malla
            faces (np.ndarray): Caras de la malla
            
        Returns:
            Dict: Resultado completo de la validación
        """
        logger.info("Iniciando validación para impresión 3D...")
        
        validation_result = {
            'is_printable': True,
            'critical_errors': [],
            'warnings': [],
            'recommendations': [],
            'statistics': {},
            'fixes_applied': []
        }
        
        try:
            # 1. Validaciones básicas de malla
            mesh_validation = self._validate_mesh_integrity(vertices, faces)
            validation_result.update(mesh_validation)
            
            # 2. Validar dimensiones
            size_validation = self._validate_print_dimensions(vertices)
            validation_result['warnings'].extend(size_validation['warnings'])
            validation_result['recommendations'].extend(size_validation['recommendations'])
            
            # 3. Validar grosor de paredes
            thickness_validation = self._validate_wall_thickness(vertices, faces)
            validation_result['warnings'].extend(thickness_validation['warnings'])
            
            # 4. Validar voladizos
            overhang_validation = self._validate_overhangs(vertices, faces)
            validation_result['warnings'].extend(overhang_validation['warnings'])
            
            # 5. Validar características pequeñas
            feature_validation = self._validate_small_features(vertices, faces)
            validation_result['warnings'].extend(feature_validation['warnings'])
            
            # 6. Generar estadísticas
            validation_result['statistics'] = self._generate_print_statistics(vertices, faces)
            
            # Determinar si es imprimible
            if validation_result['critical_errors']:
                validation_result['is_printable'] = False
            
            logger.info(f"Validación completada. Imprimible: {validation_result['is_printable']}")
            
        except Exception as e:
            logger.error(f"Error durante validación: {e}")
            validation_result['is_printable'] = False
            validation_result['critical_errors'].append(f"Error en validación: {e}")
        
        return validation_result
    
    def _validate_mesh_integrity(self, vertices: np.ndarray, faces: np.ndarray) -> Dict:
        """Valida la integridad básica de la malla."""
        result = {
            'critical_errors': [],
            'warnings': []
        }
        
        # Verificar que hay datos
        if len(vertices) == 0:
            result['critical_errors'].append("La malla no tiene vértices")
            return result
        
        if len(faces) == 0:
            result['critical_errors'].append("La malla no tiene caras")
            return result
        
        # Verificar índices de caras válidos
        max_vertex_index = len(vertices) - 1
        invalid_faces = faces[np.any(faces > max_vertex_index, axis=1)]
        
        if len(invalid_faces) > 0:
            result['critical_errors'].append(f"Se encontraron {len(invalid_faces)} caras con índices inválidos")
        
        # Verificar caras degeneradas
        degenerate_count = self._count_degenerate_faces(vertices, faces)
        if degenerate_count > 0:
            result['warnings'].append(f"Se encontraron {degenerate_count} caras degeneradas")
        
        # Verificar vértices duplicados
        duplicate_count = self._count_duplicate_vertices(vertices)
        if duplicate_count > 0:
            result['warnings'].append(f"Se encontraron {duplicate_count} vértices duplicados")
        
        return result
    
    def _validate_print_dimensions(self, vertices: np.ndarray) -> Dict:
        """Valida las dimensiones para impresión."""
        result = {
            'warnings': [],
            'recommendations': []
        }
        
        # Calcular dimensiones
        bbox_min = np.min(vertices, axis=0)
        bbox_max = np.max(vertices, axis=0)
        dimensions = bbox_max - bbox_min
        max_dimension = np.max(dimensions)
        min_dimension = np.min(dimensions)
        
        # Verificar tamaño máximo
        if max_dimension > self.config['max_print_size']:
            result['warnings'].append(
                f"El modelo es demasiado grande ({max_dimension:.1f}mm). "
                f"Máximo recomendado: {self.config['max_print_size']}mm"
            )
            scale_factor = self.config['max_print_size'] / max_dimension
            result['recommendations'].append(f"Aplicar escala de {scale_factor:.3f}")
        
        # Verificar tamaño mínimo
        if max_dimension < self.config['min_print_size']:
            result['warnings'].append(
                f"El modelo es muy pequeño ({max_dimension:.1f}mm). "
                f"Mínimo recomendado: {self.config['min_print_size']}mm"
            )
            scale_factor = self.config['min_print_size'] / max_dimension
            result['recommendations'].append(f"Aplicar escala de {scale_factor:.3f}")
        
        # Verificar relación de aspecto
        aspect_ratio = max_dimension / min_dimension
        if aspect_ratio > 10:
            result['warnings'].append(
                f"Relación de aspecto alta ({aspect_ratio:.1f}:1). "
                "Puede causar problemas de estabilidad durante la impresión"
            )
        
        return result
    
    def _validate_wall_thickness(self, vertices: np.ndarray, faces: np.ndarray) -> Dict:
        """Valida el grosor de las paredes."""
        result = {'warnings': []}
        
        # Esta es una implementación simplificada
        # Una validación real requeriría análisis más complejo de la geometría
        
        # Calcular distancias entre vértices adyacentes
        edge_lengths = []
        
        for face in faces:
            for i in range(3):
                v1 = vertices[face[i]]
                v2 = vertices[face[(i + 1) % 3]]
                edge_length = np.linalg.norm(v2 - v1)
                edge_lengths.append(edge_length)
        
        min_edge_length = np.min(edge_lengths)
        
        if min_edge_length < self.config['min_wall_thickness']:
            result['warnings'].append(
                f"Algunas características son muy delgadas ({min_edge_length:.2f}mm). "
                f"Grosor mínimo recomendado: {self.config['min_wall_thickness']}mm"
            )
        
        return result
    
    def _validate_overhangs(self, vertices: np.ndarray, faces: np.ndarray) -> Dict:
        """Valida ángulos de voladizo."""
        result = {'warnings': []}
        
        # Calcular normales de caras
        normals = self._calculate_face_normals(vertices, faces)
        
        # Vector hacia arriba
        up_vector = np.array([0, 0, 1])
        
        # Calcular ángulos con respecto a la vertical
        angles = []
        for normal in normals:
            angle = np.arccos(np.dot(normal, up_vector)) * 180 / np.pi
            angles.append(angle)
        
        # Contar caras con voladizos problemáticos
        overhang_faces = np.sum(np.array(angles) > (90 - self.config['max_overhang_angle']))
        
        if overhang_faces > 0:
            result['warnings'].append(
                f"Se encontraron {overhang_faces} caras con voladizos > {self.config['max_overhang_angle']}°. "
                "Pueden requerir soporte durante la impresión"
            )
        
        return result
    
    def _validate_small_features(self, vertices: np.ndarray, faces: np.ndarray) -> Dict:
        """Valida características pequeñas que pueden no imprimirse bien."""
        result = {'warnings': []}
        
        # Calcular áreas de caras
        areas = []
        for face in faces:
            v1, v2, v3 = vertices[face]
            area = 0.5 * np.linalg.norm(np.cross(v2 - v1, v3 - v1))
            areas.append(area)
        
        min_printable_area = (self.config['min_feature_size'] ** 2) / 2
        small_faces = np.sum(np.array(areas) < min_printable_area)
        
        if small_faces > 0:
            result['warnings'].append(
                f"Se encontraron {small_faces} caras muy pequeñas. "
                f"Pueden no imprimirse correctamente (tamaño mínimo: {self.config['min_feature_size']}mm)"
            )
        
        return result
    
    def _count_degenerate_faces(self, vertices: np.ndarray, faces: np.ndarray) -> int:
        """Cuenta caras degeneradas (área cero)."""
        degenerate_count = 0
        
        for face in faces:
            v1, v2, v3 = vertices[face]
            
            # Calcular área del triángulo
            edge1 = v2 - v1
            edge2 = v3 - v1
            cross = np.cross(edge1, edge2)
            area = 0.5 * np.linalg.norm(cross)
            
            if area < 1e-10:  # Área prácticamente cero
                degenerate_count += 1
        
        return degenerate_count
    
    def _count_duplicate_vertices(self, vertices: np.ndarray, tolerance: float = 1e-6) -> int:
        """Cuenta vértices duplicados."""
        # Implementación simple usando diferencias
        duplicate_count = 0
        
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                distance = np.linalg.norm(vertices[i] - vertices[j])
                if distance < tolerance:
                    duplicate_count += 1
        
        return duplicate_count
    
    def _calculate_face_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Calcula las normales de las caras."""
        normals = []
        
        for face in faces:
            v1, v2, v3 = vertices[face]
            
            # Vectores de los bordes
            edge1 = v2 - v1
            edge2 = v3 - v1
            
            # Normal usando producto cruz
            normal = np.cross(edge1, edge2)
            
            # Normalizar
            norm_length = np.linalg.norm(normal)
            if norm_length > 0:
                normal = normal / norm_length
            
            normals.append(normal)
        
        return np.array(normals)
    
    def _generate_print_statistics(self, vertices: np.ndarray, faces: np.ndarray) -> Dict:
        """Genera estadísticas para impresión."""
        bbox_min = np.min(vertices, axis=0)
        bbox_max = np.max(vertices, axis=0)
        dimensions = bbox_max - bbox_min
        
        # Calcular volumen aproximado
        volume = 0
        for face in faces:
            v1, v2, v3 = vertices[face]
            # Volumen del tetraedro formado por el origen y el triángulo
            volume += np.abs(np.dot(v1, np.cross(v2, v3))) / 6
        
        # Calcular área superficial
        surface_area = 0
        for face in faces:
            v1, v2, v3 = vertices[face]
            area = 0.5 * np.linalg.norm(np.cross(v2 - v1, v3 - v1))
            surface_area += area
        
        # Estimar tiempo y material de impresión
        estimated_time_hours = volume / 1000  # Estimación muy aproximada
        estimated_filament_meters = (volume / 1000) * 3.5  # Estimación aproximada
        
        statistics = {
            'dimensions_mm': dimensions.tolist(),
            'volume_mm3': volume,
            'surface_area_mm2': surface_area,
            'estimated_print_time_hours': estimated_time_hours,
            'estimated_filament_meters': estimated_filament_meters,
            'num_vertices': len(vertices),
            'num_faces': len(faces),
            'bbox_min': bbox_min.tolist(),
            'bbox_max': bbox_max.tolist()
        }
        
        return statistics
    
    def suggest_print_settings(self, validation_result: Dict) -> Dict:
        """Sugiere configuraciones de impresión basadas en la validación."""
        settings = {
            'layer_height': self.config['layer_height'],
            'infill_percentage': 20,
            'print_speed': 50,  # mm/s
            'supports_needed': False,
            'bed_adhesion': 'brim',
            'special_considerations': []
        }
        
        # Analizar advertencias para ajustar configuraciones
        warnings = validation_result.get('warnings', [])
        
        for warning in warnings:
            if 'voladizo' in warning.lower():
                settings['supports_needed'] = True
                settings['special_considerations'].append("Usar soportes para voladizos")
            
            if 'pequeño' in warning.lower():
                settings['layer_height'] = 0.1  # Capa más fina para detalles
                settings['print_speed'] = 30     # Velocidad más lenta
                settings['special_considerations'].append("Usar configuración de alta calidad")
            
            if 'grande' in warning.lower():
                settings['bed_adhesion'] = 'raft'
                settings['special_considerations'].append("Usar raft para mejor adhesión")
        
        return settings
