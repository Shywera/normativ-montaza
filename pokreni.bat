@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" goto build
.venv\Scripts\python.exe -c "import streamlit" 1>nul 2>nul
if errorlevel 1 goto rebuild
goto run

:rebuild
echo Postojece okruzenje ne radi - gradim ponovo...
rmdir /s /q ".venv" 2>nul

:build
echo Kreiram okruzenje i instaliram ovisnosti (jednom, ~1-2 min)...
py -3 -m venv .venv
if errorlevel 1 goto nopy
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt

:run
echo.
echo Pokrecem Normativi aplikaciju...
.venv\Scripts\python -m streamlit run app.py
pause
goto :eof

:nopy
echo.
echo GRESKA: Python nije pronadjen ("py" ne radi).
echo Instaliraj Python 3 s python.org i ukljuci "Add Python to PATH".
pause
