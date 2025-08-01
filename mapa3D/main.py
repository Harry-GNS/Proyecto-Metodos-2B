"""
Archivo principal de entrada para la aplicación Mapa 3D del Ecuador
===================================================================

Este script inicia la aplicación con interfaz gráfica para generar
modelos 3D imprimibles de la topografía del Ecuador.
"""

import sys
import os
import logging

# Agregar el directorio src al path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from gui.main_window import MainWindow
    from utils.helpers import setup_logging
    from utils.config import GUI_CONFIG, PROCESSING_CONFIG
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que todas las dependencias estén instaladas.")
    print("Ejecuta: pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """
    Verifica que las dependencias críticas estén instaladas.
    
    Returns:
        bool: True si todas las dependencias están disponibles
    """
    critical_deps = [
        ('numpy', 'numpy'),
        ('tkinter', 'tkinter'),
        ('matplotlib', 'matplotlib.pyplot'),
        ('scipy', 'scipy'),
    ]
    
    missing_deps = []
    
    for dep_name, import_name in critical_deps:
        try:
            __import__(import_name)
        except ImportError:
            missing_deps.append(dep_name)
    
    if missing_deps:
        print("ERROR: Faltan las siguientes dependencias críticas:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPara instalar las dependencias, ejecuta:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Función principal de la aplicación."""
    
    print("=" * 60)
    print("🗺️  MAPA 3D DEL ECUADOR - GENERADOR")
    print("   Proyecto de Métodos Numéricos")
    print("=" * 60)
    print()
    
    # Verificar dependencias
    print("🔍 Verificando dependencias...")
    if not check_dependencies():
        return 1
    print("✅ Dependencias críticas verificadas")
    print()
    
    # Configurar logging
    try:
        log_level = PROCESSING_CONFIG.get('logging_level', 'INFO')
        setup_logging(level=log_level)
        print(f"📝 Sistema de logging configurado (nivel: {log_level})")
    except Exception as e:
        # Fallback a configuración básica
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        print(f"📝 Sistema de logging configurado (básico): {e}")
    
    print()
    
    # Verificar y crear directorios necesarios
    print("📁 Verificando estructura de directorios...")
    try:
        directories = [
            os.path.join(current_dir, 'data', 'raw'),
            os.path.join(current_dir, 'data', 'processed'),
            os.path.join(current_dir, 'data', 'output'),
            PROCESSING_CONFIG.get('temp_dir', os.path.join(current_dir, 'temp'))
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        print("✅ Estructura de directorios verificada")
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudo crear algunos directorios: {e}")
    
    print()
    
    # Mostrar información del sistema
    try:
        import platform
        print("💻 Información del sistema:")
        print(f"   Sistema Operativo: {platform.system()} {platform.release()}")
        print(f"   Python: {platform.python_version()}")
        print(f"   Arquitectura: {platform.machine()}")
    except Exception as e:
        print(f"⚠️  No se pudo obtener información del sistema: {e}")
    
    print()
    
    # Inicializar y ejecutar aplicación
    try:
        print("🚀 Iniciando aplicación...")
        print("   Puedes cerrar esta ventana de consola después de que se abra la interfaz gráfica")
        print()
        
        app = MainWindow()
        app.run()
        
        print("\n👋 Aplicación cerrada correctamente")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Aplicación interrumpida por el usuario")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error crítico al ejecutar la aplicación: {e}")
        
        # Mostrar información adicional para debugging
        import traceback
        print("\n🔧 Información técnica para resolución de problemas:")
        print("-" * 50)
        traceback.print_exc()
        print("-" * 50)
        
        print("\n💡 Posibles soluciones:")
        print("1. Verifica que todas las dependencias estén instaladas:")
        print("   pip install -r requirements.txt")
        print("2. Asegúrate de que el entorno Python sea compatible (3.8+)")
        print("3. Si el problema persiste, revisa los logs para más detalles")
        
        return 1


if __name__ == "__main__":
    # Configurar el entorno
    try:
        # Cambiar al directorio del proyecto
        os.chdir(current_dir)
        
        # Ejecutar aplicación
        exit_code = main()
        
        # Pausa para que el usuario pueda ver los mensajes
        if exit_code != 0:
            input("\nPresiona Enter para cerrar...")
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\nError fatal: {e}")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)
