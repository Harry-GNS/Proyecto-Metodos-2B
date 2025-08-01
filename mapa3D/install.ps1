# Script de instalación para Mapa 3D del Ecuador
# ===============================================
# 
# Este script automatiza la instalación de dependencias
# para el proyecto de generación de mapas 3D del Ecuador.

# Verificar versión de Python
Write-Host "=== INSTALADOR MAPA 3D DEL ECUADOR ===" -ForegroundColor Green
Write-Host ""

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        
        if ($major -ge 3 -and $minor -ge 8) {
            Write-Host "✓ Python $pythonVersion encontrado" -ForegroundColor Green
        } else {
            Write-Host "✗ Se requiere Python 3.8 o superior. Encontrado: $pythonVersion" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "✗ Python no encontrado. Por favor instala Python 3.8+ desde python.org" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Crear entorno virtual
Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv_mapa3d") {
    Write-Host "El entorno virtual ya existe. ¿Deseas recrearlo? (s/N): " -NoNewline -ForegroundColor Cyan
    $recreate = Read-Host
    if ($recreate -eq "s" -or $recreate -eq "S") {
        Remove-Item -Recurse -Force "venv_mapa3d"
        python -m venv venv_mapa3d
        Write-Host "✓ Entorno virtual recreado" -ForegroundColor Green
    } else {
        Write-Host "✓ Usando entorno virtual existente" -ForegroundColor Green
    }
} else {
    python -m venv venv_mapa3d
    Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
}

Write-Host ""

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& "venv_mapa3d\Scripts\Activate.ps1"

# Actualizar pip
Write-Host "Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✓ pip actualizado" -ForegroundColor Green

Write-Host ""

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
Write-Host "Esto puede tomar varios minutos..." -ForegroundColor Cyan

# Dependencias básicas primero
$basicDeps = @(
    "numpy>=1.21.0",
    "matplotlib>=3.5.0",
    "scipy>=1.8.0",
    "Pillow>=9.0.0",
    "tqdm>=4.64.0"
)

Write-Host "Instalando dependencias básicas..." -ForegroundColor Cyan
foreach ($dep in $basicDeps) {
    Write-Host "  Instalando $dep..." -NoNewline
    pip install $dep --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ✗" -ForegroundColor Red
    }
}

# Dependencias de interfaz
Write-Host "Instalando dependencias de interfaz..." -ForegroundColor Cyan
pip install PyQt5>=5.15.0 --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PyQt5 instalado" -ForegroundColor Green
} else {
    Write-Host "⚠ Error con PyQt5, intentando tkinter (incluido en Python)" -ForegroundColor Yellow
}

# Dependencias 3D
Write-Host "Instalando dependencias para mallas 3D..." -ForegroundColor Cyan
$meshDeps = @(
    "numpy-stl>=3.0.0",
    "trimesh>=3.15.0",
    "meshio>=5.3.0",
    "scikit-image>=0.19.0"
)

foreach ($dep in $meshDeps) {
    Write-Host "  Instalando $dep..." -NoNewline
    pip install $dep --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ✗" -ForegroundColor Red
    }
}

# Dependencias geoespaciales (opcionales pero recomendadas)
Write-Host "Instalando dependencias geoespaciales..." -ForegroundColor Cyan
$geoDeps = @(
    "shapely>=1.8.0",
    "rasterio>=1.3.0",
    "geopandas>=0.12.0"
)

foreach ($dep in $geoDeps) {
    Write-Host "  Instalando $dep..." -NoNewline
    pip install $dep --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ⚠ (opcional)" -ForegroundColor Yellow
    }
}

# GDAL es complicado, intentar instalación alternativa
Write-Host "Intentando instalar GDAL..." -ForegroundColor Cyan
pip install GDAL --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ GDAL instalado" -ForegroundColor Green
} else {
    Write-Host "⚠ GDAL no instalado (opcional, pero recomendado)" -ForegroundColor Yellow
    Write-Host "  Para instalarlo manualmente:" -ForegroundColor Cyan
    Write-Host "  1. Instala OSGeo4W desde osgeo.org" -ForegroundColor Cyan
    Write-Host "  2. O usa conda: conda install -c conda-forge gdal" -ForegroundColor Cyan
}

Write-Host ""

# Dependencias de desarrollo (opcionales)
Write-Host "¿Instalar dependencias de desarrollo? (s/N): " -NoNewline -ForegroundColor Cyan
$devDeps = Read-Host
if ($devDeps -eq "s" -or $devDeps -eq "S") {
    Write-Host "Instalando dependencias de desarrollo..." -ForegroundColor Yellow
    pip install pytest>=7.0.0 flake8>=4.0.0 --quiet
    Write-Host "✓ Dependencias de desarrollo instaladas" -ForegroundColor Green
}

Write-Host ""

# Verificar instalación
Write-Host "Verificando instalación..." -ForegroundColor Yellow

$testScript = @"
import sys
import importlib

dependencias = [
    ('numpy', 'Procesamiento numérico'),
    ('matplotlib', 'Gráficos y visualización'),
    ('scipy', 'Algoritmos científicos'),
    ('tkinter', 'Interfaz gráfica'),
    ('PIL', 'Procesamiento de imágenes'),
    ('stl', 'Exportación STL'),
    ('trimesh', 'Manipulación de mallas'),
]

print("Verificando dependencias críticas:")
faltantes = []

for modulo, descripcion in dependencias:
    try:
        importlib.import_module(modulo)
        print(f"✓ {modulo} - {descripcion}")
    except ImportError:
        print(f"✗ {modulo} - {descripcion} - FALTANTE")
        faltantes.append(modulo)

if faltantes:
    print(f"\nFaltan {len(faltantes)} dependencias críticas.")
    sys.exit(1)
else:
    print(f"\n¡Todas las dependencias críticas están instaladas!")
    sys.exit(0)
"@

$testScript | python
$verificationResult = $LASTEXITCODE

Write-Host ""

if ($verificationResult -eq 0) {
    Write-Host "=== INSTALACIÓN COMPLETADA EXITOSAMENTE ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para usar la aplicación:" -ForegroundColor Cyan
    Write-Host "1. Activa el entorno virtual: venv_mapa3d\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "2. Ejecuta la aplicación: python main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "¿Deseas crear un acceso directo en el escritorio? (s/N): " -NoNewline -ForegroundColor Cyan
    $createShortcut = Read-Host
    
    if ($createShortcut -eq "s" -or $createShortcut -eq "S") {
        $currentPath = Get-Location
        $shortcutPath = "$env:USERPROFILE\Desktop\Mapa3D Ecuador.lnk"
        $targetPath = "$currentPath\run_mapa3d.bat"
        
        # Crear archivo batch
        $batchContent = @"
@echo off
cd /d "$currentPath"
call venv_mapa3d\Scripts\activate.bat
python main.py
pause
"@
        $batchContent | Out-File -FilePath "run_mapa3d.bat" -Encoding ASCII
        
        # Crear acceso directo
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($shortcutPath)
        $Shortcut.TargetPath = $targetPath
        $Shortcut.WorkingDirectory = $currentPath
        $Shortcut.Description = "Generador de Mapas 3D del Ecuador"
        $Shortcut.Save()
        
        Write-Host "✓ Acceso directo creado en el escritorio" -ForegroundColor Green
    }
    
} else {
    Write-Host "=== INSTALACIÓN INCOMPLETA ===" -ForegroundColor Red
    Write-Host ""
    Write-Host "Algunas dependencias no se instalaron correctamente." -ForegroundColor Yellow
    Write-Host "La aplicación podría funcionar con funcionalidad limitada." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para resolver problemas:" -ForegroundColor Cyan
    Write-Host "1. Intenta reinstalar las dependencias faltantes manualmente" -ForegroundColor White
    Write-Host "2. Considera usar conda en lugar de pip" -ForegroundColor White
    Write-Host "3. Consulta la documentación en docs/installation.md" -ForegroundColor White
}

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
