# Mapa 3D del Ecuador - Proyecto de Métodos Numéricos

## 🎯 Objetivo del Proyecto
Crear un objeto imprimible en 3D (formato STL) que represente la topografía del Ecuador continental con escala realista, utilizando datos de elevación geográfica reales.

## 📋 Estado del Proyecto

### ✅ Completado
- [x] Estructura del proyecto
- [x] Configuración inicial

### 🔄 En Desarrollo
- [ ] Fase 1: Preparación de Datos
- [ ] Fase 2: Interfaz Gráfica
- [ ] Fase 3: Generación de Malla 3D
- [ ] Fase 4: Segmentación Política
- [ ] Fase 5: Validación y Optimización

## 🚀 Instalación

1. Clona el repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
mapa3D/
├── data/                       # Datos del proyecto
│   ├── raw/                    # Datos originales
│   ├── processed/              # Datos procesados
│   └── output/                 # Modelos 3D generados
├── src/                        # Código fuente
│   ├── data_processing/        # Procesamiento de datos
│   ├── gui/                    # Interfaz gráfica
│   ├── mesh_generation/        # Generación de mallas 3D
│   ├── validation/             # Validación de modelos
│   └── utils/                  # Utilidades
├── tests/                      # Pruebas unitarias
├── docs/                       # Documentación
├── examples/                   # Ejemplos de uso
└── assets/                     # Recursos multimedia
```

## 🎯 Uso Básico

```python
from src.gui.main_window import MainWindow

# Iniciar la aplicación
app = MainWindow()
app.run()
```

## 📚 Documentación

Consulta la carpeta `docs/` para documentación detallada:
- [Instalación](docs/installation.md)
- [Guía de uso](docs/usage.md)
- [Referencia API](docs/api_reference.md)

## 🛠️ Desarrollo

Para contribuir al proyecto:
1. Ejecuta las pruebas: `python -m pytest tests/`
2. Revisa el código: `flake8 src/`
3. Actualiza la documentación según sea necesario

## 📄 Licencia

Este proyecto es desarrollado como parte del curso de Métodos Numéricos.
