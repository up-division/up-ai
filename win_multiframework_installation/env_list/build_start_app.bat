@echo off
rmdir /S /Q build
rmdir /S /Q dist
del StartAPP.spec

python -m PyInstaller --onefile --distpath C:\MyApp\dist StartAPP.py