# Guía de Instalación - Mapa 3D del Ecuador

## Requisitos del Sistema

### Sistema Operativo
- Windows 10/11 (recomendado)
- macOS 10.14 o superior
- Linux Ubuntu 18.04 o superior

### Software Requerido
- Python 3.8 o superior
- Git (opcional, para clonar el repositorio)

## Instalación Paso a Paso

### 1. Preparar el Entorno Python

```bash
# Verificar versión de Python
python --version

# Crear entorno virtual (recomendado)
python -m venv venv_mapa3d

# Activar entorno virtual
# En Windows:
venv_mapa3d\Scripts\activate

# En macOS/Linux:
source venv_mapa3d/bin/activate
```

### 2. Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias desde requirements.txt
pip install -r requirements.txt
```

### 3. Instalación Manual de Dependencias (si es necesario)

Si la instalación automática falla, instalar manualmente:

```bash
# Dependencias básicas
pip install numpy>=1.21.0
pip install matplotlib>=3.5.0
pip install scipy>=1.8.0

# Dependencias geoespaciales
pip install rasterio>=1.3.0
pip install geopandas>=0.12.0
pip install shapely>=1.8.0

# Dependencias para mallas 3D
pip install numpy-stl>=3.0.0
pip install trimesh>=3.15.0
pip install meshio>=5.3.0

# Dependencias para interfaz
pip install PyQt5>=5.15.0

# Dependencias adicionales
pip install scikit-image>=0.19.0
pip install Pillow>=9.0.0
pip install tqdm>=4.64.0
```

### 4. Instalación de GDAL (Opcional pero Recomendado)

GDAL puede ser complicado de instalar. Opciones:

#### Windows:
```bash
# Opción 1: Usar conda
conda install -c conda-forge gdal

# Opción 2: Usar wheels precompilados
pip install --find-links https://girder.github.io/large_image_wheels GDAL
```

#### macOS:
```bash
# Usar Homebrew
brew install gdal
pip install gdal
```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev
pip install gdal
```

### 5. Verificar Instalación

Ejecutar script de verificación:

```python
# verificar_instalacion.py
import sys

dependencias = [
    'numpy',
    'matplotlib',
    'scipy',
    'rasterio',
    'shapely',
    'stl',
    'trimesh',
    'tkinter'
]

print("Verificando dependencias...")
faltantes = []

for dep in dependencias:
    try:
        __import__(dep)
        print(f"✓ {dep}")
    except ImportError:
        print(f"✗ {dep} - FALTANTE")
        faltantes.append(dep)

if faltantes:
    print(f"\nFaltan {len(faltantes)} dependencias:")
    for dep in faltantes:
        print(f"  - {dep}")
else:
    print("\n¡Todas las dependencias están instaladas!")
```

## Solución de Problemas Comunes

### Error: "Microsoft Visual C++ 14.0 is required"
**Solución:** Instalar Microsoft Visual C++ Build Tools
- Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Error con GDAL
**Solución:** Usar conda en lugar de pip
```bash
conda install -c conda-forge gdal rasterio geopandas
```

### Error con PyQt5
**Solución:** Instalar dependencias del sistema
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt5

# macOS
brew install pyqt5
```

### Error: "Could not find a version that satisfies the requirement"
**Solución:** Actualizar pip y setuptools
```bash
python -m pip install --upgrade pip setuptools wheel
```

## Instalación de Software Adicional

### Para Validación de Modelos STL

#### PrusaSlicer (Gratuito)
1. Descargar desde: https://www.prusa3d.com/prusaslicer/
2. Instalar siguiendo las instrucciones del instalador

#### Bambu Studio (Gratuito)
1. Descargar desde: https://bambulab.com/en/download
2. Instalar siguiendo las instrucciones del instalador

### Para Análisis Geoespacial (Opcional)

#### QGIS (Gratuito)
1. Descargar desde: https://qgis.org/en/site/forusers/download.html
2. Instalar la versión LTR (Long Term Release)

## Configuración del Proyecto

### 1. Estructura de Directorios
El proyecto debe tener la siguiente estructura:
```
mapa3D/
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
├── src/
├── tests/
├── docs/
└── examples/
```

### 2. Variables de Entorno (Opcional)
```bash
# Agregar al .bashrc o .zshrc (Linux/macOS) o variables de entorno (Windows)
export MAPA3D_DATA_DIR="/ruta/a/mapa3D/data"
export MAPA3D_TEMP_DIR="/tmp/mapa3d"
```

## Verificación Final

Ejecutar la aplicación de prueba:

```bash
cd mapa3D
python src/gui/main_window.py
```

Si la ventana de la aplicación se abre correctamente, la instalación está completa.

## Desinstalación

Para desinstalar completamente:

```bash
# Desactivar entorno virtual
deactivate

# Eliminar entorno virtual
rm -rf venv_mapa3d  # Linux/macOS
rmdir /s venv_mapa3d  # Windows

# Eliminar archivos del proyecto
rm -rf mapa3D  # Linux/macOS
rmdir /s mapa3D  # Windows
```

## Soporte

Si encuentras problemas durante la instalación:

1. Revisa los logs de error detalladamente
2. Busca el error específico en Google
3. Consulta la documentación de las dependencias problemáticas
4. Considera usar conda en lugar de pip para dependencias complejas

## Notas de Desarrollo

Para desarrolladores que quieran contribuir al proyecto:

```bash
# Instalar dependencias adicionales de desarrollo
pip install pytest>=7.0.0
pip install flake8>=4.0.0
pip install black>=22.0.0

# Ejecutar pruebas
python -m pytest tests/

# Verificar estilo de código
flake8 src/

# Formatear código
black src/
```
