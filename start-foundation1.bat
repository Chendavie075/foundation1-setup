@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE="

if exist "%~dp0env\python.exe" set "PYTHON_EXE=%~dp0env\python.exe"
if not defined PYTHON_EXE if exist "%~dp0..\env\python.exe" set "PYTHON_EXE=%~dp0..\env\python.exe"
if not defined PYTHON_EXE if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not defined PYTHON_EXE set "PYTHON_EXE=python"

echo Foundation-1 is starting...
echo Open the local URL printed below after the model finishes loading.
echo.

"%PYTHON_EXE%" run_gradio.py
if errorlevel 1 (
    echo.
    echo Foundation-1 exited with an error.
)

pause
