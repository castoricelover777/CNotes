@echo off
setlocal
cd /d "%~dp0"

pythonw "src\c_notes.py"
if %ERRORLEVEL% EQU 0 exit /b 0

pyw "src\c_notes.py"
