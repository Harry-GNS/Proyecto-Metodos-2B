# 🗺️ Mapa 3D del Ecuador - Generador Avanzado

![Banner](Banner.jpg)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Avanzado-orange.svg)](https://github.com)
[![Version](https://img.shields.io/badge/Version-2.0-brightgreen.svg)](https://github.com)

## 🎯 Descripción

Sistema avanzado para generar modelos 3D imprimibles del territorio ecuatoriano a partir de datos de elevación digital (DEM). Incluye funcionalidades avanzadas como selección de zonas específicas, procesamiento inteligente y validación para impresión 3D.

## ✨ Funcionalidades Avanzadas

### 🔄 Carga Inteligente de Datos
- **Múltiples formatos soportados**: GeoTIFF, SRTM (.hgt), ASCII Grid (.asc), XYZ
- **Explorador automático**: Escanea archivos disponibles en directorios locales
- **Generador de datos de prueba**: Crea datos sintéticos para testing
- **Carga con vista previa**: Información detallada antes de procesar

### 🎯 Selección de Zonas Geográficas
- **Zonas predefinidas**: Ecuador completo, Costa, Sierra, Oriente, regiones específicas
- **Zonas metropolitanas**: Quito, Guayaquil, Cuenca
- **Zonas volcánicas**: Volcanes principales del Ecuador
- **Selección personalizada**: Definir coordenadas exactas
- **Vista previa de bounds**: Verificación visual de la zona seleccionada

### ⚙️ Procesamiento Avanzado
- **Suavizado inteligente**: Filtros gaussianos para reducir ruido
- **Relleno de huecos**: Interpolación automática de datos faltantes
- **Escala vertical configurable**: Exageración de elevaciones para mejor visualización
- **Optimización de malla**: Reducción de triángulos manteniendo calidad
- **Resolución adaptativa**: Ajuste automático según tamaño de zona

### 🔍 Análisis y Validación
- **Estadísticas detalladas**: Análisis completo de distribución de elevaciones
- **Validación de manifold**: Verificación de estructura 3D válida
- **Análisis de imprimibilidad**: Verificación de compatibilidad con impresoras 3D
- **Reporte de calidad**: Métricas de calidad de malla generada

### 📊 Visualización
- **Vista previa 2D**: Mapas de elevación con gradientes de color
- **Vista previa 3D**: Modelo tridimensional interactivo
- **Análisis estadístico**: Gráficos de distribución y tendencias
- **Interfaz con pestañas**: Organización intuitiva de funcionalidades

## 🚀 Instalación

### Requisitos del Sistema
- Python 3.8 o superior
- Librerías geoespaciales (GDAL, rasterio)
- Librerías de procesamiento científico (NumPy, SciPy)
- Interfaz gráfica (Tkinter, matplotlib)

### Instalación Automática
```bash
# Clonar el repositorio
git clone https://github.com/usuario/mapa3D-ecuador.git
cd mapa3D-ecuador

# Ejecutar instalador
python main.py
```

El sistema detectará e instalará automáticamente las dependencias necesarias.

### Instalación Manual
```bash
pip install numpy scipy matplotlib tkinter
pip install rasterio gdal geopandas
pip install numpy-stl trimesh meshio
pip install pillow
```

## 🎮 Uso Avanzado

### 1. Carga de Datos
- **Escaneo automático**: El sistema detecta archivos DEM en la carpeta `data/`
- **Carga manual**: Seleccionar archivos específicos con el explorador
- **Datos de prueba**: Generar datos sintéticos para testing

### 2. Selección de Zona
```python
# Zonas predefinidas disponibles:
- Ecuador Completo: Todo el territorio continental
- Costa: Región costera del Pacífico
- Sierra: Cordillera de los Andes
- Oriente: Región amazónica
- Norte: Provincias del norte
- Centro: Zona central del país
- Sur: Provincias del sur
- Volcanes: Zonas volcánicas principales
- Quito Metropolitano: Área metropolitana de Quito
- Guayaquil Metropolitano: Área metropolitana de Guayaquil
```

### 3. Configuración Avanzada
- **Resolución de malla**: 50-500 puntos por lado
- **Escala vertical**: 0.1x - 5.0x exageración
- **Opciones de procesamiento**:
  - ✅ Suavizado de superficie
  - ✅ Relleno de huecos automático
  - ✅ Optimización de malla
  - ✅ Validación de manifold
  - ✅ Verificación de imprimibilidad

### 4. Generación y Exportación
1. **Procesar datos**: Aplicar filtros y configuraciones
2. **Generar malla**: Crear modelo 3D optimizado
3. **Exportar STL**: Archivo listo para Bambu Studio

## 📁 Estructura del Proyecto

```
mapa3D/
├── main.py                          # Aplicación principal
├── Banner.jpg                       # Banner del proyecto
├── README.md                        # Este archivo
├── requirements.txt                 # Dependencias
├── data/                           # Datos DEM
│   ├── raw/                        # Archivos originales
│   └── processed/                  # Datos procesados
├── src/                            # Código fuente
│   ├── gui/                        # Interfaz gráfica
│   │   ├── main_window.py          # Ventana principal avanzada
│   │   └── zone_selector.py        # Selector de zonas geográficas
│   ├── data_processing/            # Procesamiento de datos
│   │   ├── dem_loader.py           # Cargador básico DEM
│   │   ├── advanced_dem_loader.py  # Cargador avanzado multiformato
│   │   ├── ecuador_filter.py       # Filtros específicos de Ecuador
│   │   └── political_segmentation.py # Segmentación política
│   ├── mesh_generation/            # Generación de mallas 3D
│   │   ├── terrain_to_mesh.py      # Conversión terreno a malla
│   │   └── stl_exporter.py         # Exportador STL
│   ├── validation/                 # Validación y calidad
│   │   └── print_validator.py      # Validador impresión 3D
│   └── utils/                      # Utilidades
│       └── config.py               # Configuraciones
├── tests/                          # Pruebas unitarias
├── docs/                           # Documentación
├── examples/                       # Ejemplos de uso
└── output/                         # Archivos STL generados
```

## 🔧 Características Técnicas

### Formatos de Entrada Soportados
- **GeoTIFF** (`.tif`, `.tiff`): Formato estándar geoespacial
- **SRTM Height** (`.hgt`): Datos de misión topográfica
- **ASCII Grid** (`.asc`): Formato de texto estructurado
- **XYZ Point Cloud** (`.xyz`): Nube de puntos tridimensional
- **ERDAS Imagine** (`.img`): Formato de imágenes geoespaciales
- **Band Interleaved** (`.bil`): Formato raster entrelazado

### Algoritmos Implementados
- **Interpolación bilineal**: Para suavizado de superficie
- **Triangulación de Delaunay**: Generación de malla óptima
- **Filtros gaussianos**: Reducción de ruido
- **Optimización de mesh**: Reducción de complejidad
- **Validación topológica**: Verificación de manifold

### Compatibilidad de Impresión 3D
- ✅ **Bambu Studio**: Optimizado para impresoras Bambu Lab
- ✅ **PrusaSlicer**: Compatible con impresoras Prusa
- ✅ **Cura**: Funciona con impresoras FDM estándar
- ✅ **Validación automática**: Verificación de estructura imprimible

## 📊 Ejemplos de Uso

### Caso 1: Mapa del Chimborazo
```python
# Configuración recomendada para volcanes
zona = "Volcanes"
resolucion = 200
escala_z = 2.0
suavizado = True
```

### Caso 2: Quito Metropolitano
```python
# Para modelos urbanos detallados
zona = "Quito Metropolitano"
resolucion = 300
escala_z = 1.5
optimizar_malla = True
```

### Caso 3: Costa Ecuatoriana
```python
# Para regiones de baja elevación
zona = "Costa"
resolucion = 150
escala_z = 3.0
rellenar_huecos = True
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🎓 Créditos Académicos

**Proyecto Métodos Numéricos 2B - 2025A**
- Universidad: [Nombre de la Universidad]
- Curso: Métodos Numéricos
- Semestre: Cuarto Semestre 2025-A

## 📧 Contacto

Para soporte técnico o consultas académicas:
- Email: [tu-email@universidad.edu]
- GitHub Issues: [Link a issues del repositorio]

---

> 🎯 **Objetivo**: Generar modelos 3D precisos y imprimibles del territorio ecuatoriano para educación, investigación y visualización geográfica.

> 🔄 **Estado**: Versión 2.0 - Sistema completo con funcionalidades avanzadas
