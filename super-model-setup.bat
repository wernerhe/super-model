@echo off
REM Windows wrapper for super-model-setup. Double-click or run from cmd.exe.
REM Forwards all arguments to the Python script. Uses 'py' launcher first
REM (preferred on Windows; picks up the highest installed Python),
REM then falls back to 'python' on PATH.

setlocal
set SCRIPT_DIR=%~dp0

where py >nul 2>&1
if %errorlevel% equ 0 (
    py "%SCRIPT_DIR%super-model-setup.py" %*
    exit /b %errorlevel%
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    python "%SCRIPT_DIR%super-model-setup.py" %*
    exit /b %errorlevel%
)

echo ERROR: no Python found on PATH. Install Python 3.11+ and re-run. 1>&2
exit /b 1
