"""
Ejemplo básico de uso del generador de mapas 3D
==============================================

Este script demuestra el uso básico de las clases principales
del proyecto para generar un mapa 3D simple.
"""

import sys
import os
import numpy as np

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_processing.dem_loader import DEMLoader
from data_processing.ecuador_filter import EcuadorFilter
from mesh_generation.terrain_to_mesh import TerrainToMesh
from mesh_generation.stl_exporter import STLExporter
from validation.print_validation import PrintValidation
from utils.helpers import setup_logging


def main():
    """Función principal del ejemplo."""
    
    # Configurar logging
    setup_logging(level="INFO")
    
    print("=== Ejemplo Básico - Generador de Mapas 3D ===\n")
    
    # 1. Crear datos de elevación sintéticos (simulando DEM)
    print("1. Creando datos de elevación sintéticos...")
    
    # Crear una grilla simple que simule topografía
    x = np.linspace(-79.0, -77.0, 100)  # Longitudes (Ecuador)
    y = np.linspace(-1.0, 0.0, 100)     # Latitudes (Ecuador)
    X, Y = np.meshgrid(x, y)
    
    # Simular elevaciones con función matemática
    Z = 1000 + 2000 * np.sin(X * 2) * np.cos(Y * 3) + 500 * np.random.random(X.shape)
    Z = np.maximum(Z, 0)  # Asegurar elevaciones positivas
    
    print(f"   Datos generados: {Z.shape}")
    print(f"   Rango de elevaciones: {np.min(Z):.1f} - {np.max(Z):.1f} metros")
    
    # 2. Aplicar filtros del Ecuador
    print("\n2. Aplicando filtros específicos del Ecuador...")
    
    ecuador_filter = EcuadorFilter()
    
    # Aplicar filtro de rango de elevación
    Z_filtered = ecuador_filter.apply_elevation_range_filter(Z, min_elevation=0, max_elevation=4000)
    
    valid_points = np.sum(~np.isnan(Z_filtered))
    print(f"   Puntos válidos después del filtrado: {valid_points}")
    
    # 3. Generar malla 3D
    print("\n3. Generando malla 3D...")
    
    mesh_generator = TerrainToMesh()
    mesh_generator.load_elevation_data(Z_filtered, (X, Y))
    
    # Crear malla usando grilla regular
    vertices, faces = mesh_generator.create_regular_grid_mesh(
        scale_factor=0.001,  # Escalar para dimensiones apropiadas
        z_scale=0.01         # Escalar altura para impresión
    )
    
    print(f"   Malla generada: {len(vertices)} vértices, {len(faces)} caras")
    
    # Obtener estadísticas de la malla
    stats = mesh_generator.get_mesh_statistics()
    print(f"   Área superficial: {stats['surface_area']:.2f} unidades²")
    
    # 4. Validar para impresión 3D
    print("\n4. Validando modelo para impresión 3D...")
    
    validator = PrintValidation()
    validation_result = validator.validate_for_printing(vertices, faces)
    
    print(f"   ¿Es imprimible?: {validation_result['is_printable']}")
    
    if validation_result['warnings']:
        print("   Advertencias:")
        for warning in validation_result['warnings'][:3]:  # Mostrar solo las primeras 3
            print(f"     - {warning}")
    
    if validation_result['recommendations']:
        print("   Recomendaciones:")
        for rec in validation_result['recommendations'][:2]:
            print(f"     - {rec}")
    
    # 5. Exportar a STL
    print("\n5. Exportando modelo STL...")
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    stl_exporter = STLExporter()
    
    # Escalar modelo para impresión (tamaño objetivo: 100mm)
    scaled_vertices = stl_exporter.scale_for_printing(vertices, target_size=100.0)
    
    # Agregar base para impresión
    final_vertices, final_faces = stl_exporter.create_printable_base(
        scaled_vertices, faces, base_thickness=2.0
    )
    
    # Exportar archivo STL
    output_path = os.path.join(output_dir, "ecuador_ejemplo_basico.stl")
    success = stl_exporter.export_mesh_to_stl(
        final_vertices, final_faces, output_path, binary=True
    )
    
    if success:
        print(f"   ✓ STL exportado exitosamente: {output_path}")
        
        # Mostrar estadísticas finales
        file_size = os.path.getsize(output_path)
        print(f"   Tamaño del archivo: {file_size / 1024:.1f} KB")
        
        final_stats = validator._generate_print_statistics(final_vertices, final_faces)
        print(f"   Dimensiones finales: {final_stats['dimensions_mm'][0]:.1f} x "
              f"{final_stats['dimensions_mm'][1]:.1f} x {final_stats['dimensions_mm'][2]:.1f} mm")
        print(f"   Tiempo estimado de impresión: {final_stats['estimated_print_time_hours']:.1f} horas")
        
    else:
        print("   ✗ Error al exportar STL")
    
    # 6. Sugerir configuraciones de impresión
    print("\n6. Configuraciones de impresión sugeridas:")
    
    print_settings = validator.suggest_print_settings(validation_result)
    print(f"   Altura de capa: {print_settings['layer_height']}mm")
    print(f"   Relleno: {print_settings['infill_percentage']}%")
    print(f"   Velocidad: {print_settings['print_speed']}mm/s")
    print(f"   Soportes necesarios: {'Sí' if print_settings['supports_needed'] else 'No'}")
    print(f"   Adhesión a cama: {print_settings['bed_adhesion']}")
    
    if print_settings['special_considerations']:
        print("   Consideraciones especiales:")
        for consideration in print_settings['special_considerations']:
            print(f"     - {consideration}")
    
    print("\n=== Ejemplo completado exitosamente ===")
    print(f"\nPuedes encontrar el archivo STL en: {output_path}")
    print("Para imprimir, abre el archivo en tu software de slicing preferido (PrusaSlicer, Bambu Studio, etc.)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
