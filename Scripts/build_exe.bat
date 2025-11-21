@echo off
REM Script para generar el .exe con PyInstaller

cd /d "c:\Users\Abitt\Desktop\DespliegueV2\DocuSeal-main"

REM Activar el virtualenv
call "c:\Users\Abitt\Desktop\DespliegueV2\DocuSeal-main\venv\Scripts\activate.bat"

REM Ejecutar PyInstaller
python -m PyInstaller DocuSealService.spec --distpath "dist" --workpath "build" --specpath "."

pause
