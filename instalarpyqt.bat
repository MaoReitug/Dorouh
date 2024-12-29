@echo off
echo Verificando la instalación de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python no está instalado o no está en el PATH.
    echo Por favor, instala Python y asegúrate de que esté configurado en el PATH.
    pause
    exit /b
)

echo Instalando PyQt5...
pip install PyQt5
if errorlevel 1 (
    echo Hubo un problema instalando PyQt5. Verifica tu conexión a Internet o el entorno de Python.
    pause
    exit /b
)

echo PyQt5 instalado correctamente.
pause
