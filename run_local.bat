@echo off
setlocal

cd /d "%~dp0"

echo.
echo ========================================
echo   RunWise AI - Local Streamlit Launcher
echo ========================================
echo.

call :find_python
if defined PYTHON_CMD goto :python_found

echo Python was not found on PATH or in common install locations.
echo.
echo Choose an option:
echo   I - Install Python 3.12 using winget
echo   D - Open the Python download page manually
echo   Q - Quit
echo.
choice /C IDQ /N /M "Press I, D, or Q: "
if errorlevel 3 exit /b 1
if errorlevel 2 goto :open_download
if errorlevel 1 goto :install_python

:python_found
echo Using Python command: %PYTHON_CMD%
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

echo Installing/updating requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Starting RunWise AI locally...
echo Open this URL if your browser does not open automatically:
echo http://localhost:8501
echo.

python -m streamlit run streamlit_app.py

echo.
echo RunWise AI stopped.
pause

exit /b 0

:find_python
where python >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
    exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
    exit /b 0
)

where python3 >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=python3"
    exit /b 0
)

for %%P in (
    "%LocalAppData%\Programs\Python\Python312\python.exe"
    "%LocalAppData%\Programs\Python\Python311\python.exe"
    "%LocalAppData%\Programs\Python\Python310\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles(x86)%\Python312\python.exe"
    "%ProgramFiles(x86)%\Python311\python.exe"
    "%ProgramFiles(x86)%\Python310\python.exe"
) do (
    if exist %%P (
        set "PYTHON_CMD=%%P"
        exit /b 0
    )
)

exit /b 0

:install_python
where winget >nul 2>nul
if errorlevel 1 (
    echo.
    echo winget was not found on this PC.
    goto :open_download
)

echo.
echo Installing Python 3.12 with winget...
winget install --id Python.Python.3.12 -e --source winget
if errorlevel 1 (
    echo Python installation did not complete successfully.
    echo You can install it manually from the download page.
    goto :open_download
)

echo.
echo Python installed. Restarting launcher checks...
call :find_python
if defined PYTHON_CMD goto :python_found

echo Python installed, but this terminal cannot see it yet.
echo Close this window and double-click run_local.bat again.
pause
exit /b 1

:open_download
echo.
echo Opening Python downloads page...
start "" "https://www.python.org/downloads/"
echo.
echo During installation, check: Add python.exe to PATH
echo Then close this window and double-click run_local.bat again.
pause
exit /b 1
