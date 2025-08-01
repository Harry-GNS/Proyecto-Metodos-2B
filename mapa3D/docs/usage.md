# Guía de Uso - Mapa 3D del Ecuador

## Inicio Rápido

### 1. Ejecutar la Aplicación

```bash
cd mapa3D
python src/gui/main_window.py
```

### 2. Flujo de Trabajo Básico

1. **Cargar datos DEM** → Seleccionar archivo de elevación
2. **Configurar parámetros** → Ajustar región, resolución y escala
3. **Procesar datos** → Filtrar y preparar datos para malla 3D
4. **Generar malla** → Crear modelo 3D triangular
5. **Exportar STL** → Guardar archivo para impresión 3D

## Interfaz de Usuario

### Ventana Principal

La interfaz está dividida en 4 secciones principales:

#### 1. Carga de Datos DEM
- **Examinar**: Seleccionar archivo DEM (.tif, .tiff)
- **Cargar DEM**: Procesar el archivo seleccionado
- **Información**: Muestra estadísticas del archivo cargado

#### 2. Configuración
- **Región**: Ecuador Continental, Costa, Sierra, Oriente
- **Resolución**: Baja, Media, Alta
- **Escala Z**: Factor de exageración vertical (0.1 - 10.0)
- **Suavizado**: Aplicar algoritmos de suavizado

#### 3. Procesamiento
- **Procesar Datos**: Aplicar filtros y preparar datos
- **Generar Malla 3D**: Crear modelo triangular
- **Exportar STL**: Guardar archivo para impresión
- **Vista Previa**: Visualizar modelo 3D

#### 4. Registro de Actividad
- Muestra el progreso y mensajes del sistema
- Errores y advertencias
- Estadísticas de procesamiento

## Formatos de Datos Soportados

### Entrada (DEM)
- **GeoTIFF** (.tif, .tiff) - Recomendado
- **HGT** (.hgt) - Archivos SRTM
- **IMG** (.img) - Archivos ERDAS IMAGINE

### Salida (Modelos 3D)
- **STL** (.stl) - Para impresión 3D
- **OBJ** (.obj) - Para visualización y edición
- **PLY** (.ply) - Para análisis científico

## Configuraciones Detalladas

### Región de Procesamiento

#### Ecuador Continental
- Incluye las 23 provincias continentales
- Excluye Galápagos automáticamente
- Coordenadas: 81°W - 75°W, 5°S - 1.5°N

#### Regiones Específicas

**Costa**
- Provincias: Esmeraldas, Manabí, Los Ríos, Guayas, Santa Elena, El Oro
- Elevación típica: 0 - 1000m
- Características: Llanuras costeras, cordillera costanera

**Sierra**
- Provincias: Carchi, Imbabura, Pichincha, Cotopaxi, Tungurahua, Chimborazo, Bolívar, Cañar, Azuay, Loja
- Elevación típica: 1000 - 6000m
- Características: Andes, volcanes, valles interandinos

**Oriente**
- Provincias: Sucumbíos, Napo, Orellana, Pastaza, Morona Santiago, Zamora Chinchipe
- Elevación típica: 200 - 2000m
- Características: Selva amazónica, ríos, colinas

### Resolución de Procesamiento

#### Baja (Rápida)
- Decimación: 1:4
- Vértices aprox.: 10,000 - 50,000
- Tiempo: 1-5 minutos
- Uso: Vista previa, pruebas rápidas

#### Media (Equilibrada)
- Decimación: 1:2
- Vértices aprox.: 50,000 - 200,000
- Tiempo: 5-15 minutos
- Uso: Modelos estándar de impresión

#### Alta (Detallada)
- Sin decimación
- Vértices aprox.: 200,000 - 1,000,000
- Tiempo: 15-60 minutos
- Uso: Modelos de alta calidad, análisis detallado

### Factor de Escala Z

- **0.1 - 0.5**: Muy comprimido (mejor para áreas montañosas)
- **0.5 - 1.0**: Comprimido (equilibrio general)
- **1.0**: Escala real (proporción 1:1)
- **1.0 - 3.0**: Exagerado (resalta características sutiles)
- **3.0 - 10.0**: Muy exagerado (dramático, educativo)

## Flujo de Trabajo Avanzado

### 1. Preparación de Datos

#### Verificar Calidad de Datos DEM
```python
# En el registro verás:
# - Rango de elevaciones
# - Valores faltantes (NoData)
# - Resolución espacial
# - Sistema de coordenadas
```

#### Aplicar Filtros
- Rango de elevación válido: -500m a 7000m
- Eliminación de valores atípicos
- Suavizado gaussian (opcional)

### 2. Generación de Malla

#### Algoritmo Regular Grid
- Más rápido
- Conserva estructura original
- Mejor para datos uniformes

#### Algoritmo Delaunay
- Más lento pero flexible
- Optimiza triángulos
- Mejor para datos irregulares

### 3. Optimización para Impresión

#### Validaciones Automáticas
- Dimensiones apropiadas (5mm - 200mm)
- Grosor de paredes (>0.8mm)
- Ángulos de voladizo (<45°)
- Características pequeñas (>0.4mm)

#### Correcciones Sugeridas
- Escalado automático
- Adición de base de impresión
- Reparación de malla
- Optimización de archivos

## Ejemplos de Uso

### Ejemplo 1: Mapa Básico del Ecuador

```python
# 1. Cargar DEM del Ecuador completo
# 2. Configurar:
#    - Región: Ecuador Continental
#    - Resolución: Media
#    - Escala Z: 2.0 (exagerado para mostrar relieves)
#    - Suavizado: Activado
# 3. Procesar y exportar
```

### Ejemplo 2: Volcán Chimborazo Detallado

```python
# 1. Cargar DEM de alta resolución de Chimborazo
# 2. Configurar:
#    - Región: Sierra (recortar manualmente)
#    - Resolución: Alta
#    - Escala Z: 1.0 (escala real)
#    - Suavizado: Desactivado
# 3. Validar para impresión
```

### Ejemplo 3: Perfil Educativo Costa-Sierra-Oriente

```python
# 1. Cargar DEM de transecto específico
# 2. Configurar:
#    - Región: Ecuador Continental
#    - Resolución: Media
#    - Escala Z: 5.0 (muy exagerado)
#    - Suavizado: Activado
# 3. Generar modelo alargado para mostrar diferencias
```

## Solución de Problemas

### Problemas Comunes

#### "Archivo DEM muy grande"
**Solución:**
- Usar resolución "Baja" primero
- Considerar recortar el área manualmente
- Verificar memoria RAM disponible

#### "Malla con agujeros"
**Solución:**
- Revisar valores NoData en DEM original
- Aplicar interpolación en QGIS
- Usar algoritmo de triangulación Delaunay

#### "Modelo muy pequeño/grande para impresión"
**Solución:**
- Ajustar factor de escala automáticamente
- Verificar dimensiones en vista previa
- Usar escalado personalizado

#### "Tiempo de procesamiento excesivo"
**Solución:**
- Reducir resolución
- Procesar por regiones más pequeñas
- Verificar especificaciones del computador

### Optimización de Rendimiento

#### Hardware Recomendado
- **RAM**: 8GB mínimo, 16GB recomendado
- **CPU**: 4 núcleos mínimo
- **Almacenamiento**: 5GB espacio libre

#### Software
- Cerrar aplicaciones innecesarias
- Usar SSD para datos temporales
- Monitorear uso de memoria

## Validación de Resultados

### Verificaciones Antes de Imprimir

1. **Dimensiones Físicas**
   - Verificar que cabe en la impresora
   - Comprobar relación de aspecto

2. **Calidad de Malla**
   - Sin agujeros o intersecciones
   - Normales consistentes
   - Manifold cerrado

3. **Características de Impresión**
   - Grosor de paredes adecuado
   - Ángulos de voladizo aceptables
   - Detalles imprimibles

### Herramientas de Validación Externa

#### PrusaSlicer
- Reparación automática de STL
- Vista previa de impresión
- Estimación de tiempo y material

#### Bambu Studio
- Análisis de imprimibilidad
- Soporte automático
- Configuraciones optimizadas

## Casos de Uso Educativo

### Para Geografía
- Mostrar diferencias topográficas
- Comprender escalas geográficas
- Visualizar fenómenos geológicos

### Para Geología
- Analizar formaciones montañosas
- Estudiar patrones de drenaje
- Identificar estructuras tectónicas

### Para Cartografía
- Entender proyecciones cartográficas
- Comparar representaciones 2D vs 3D
- Analizar distorsiones de mapas

## Recursos Adicionales

### Datos DEM Gratuitos
- **SRTM**: https://earthexplorer.usgs.gov/
- **ALOS World 3D**: https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm
- **OpenTopography**: https://opentopography.org/

### Software Complementario
- **QGIS**: Procesamiento geoespacial
- **MeshLab**: Edición avanzada de mallas
- **Blender**: Modelado y renderizado 3D

### Comunidades y Soporte
- Foros de impresión 3D
- Grupos de GIS y cartografía
- Comunidades educativas de geografía
