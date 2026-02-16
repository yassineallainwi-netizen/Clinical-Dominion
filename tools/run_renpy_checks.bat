@echo off
setlocal enabledelayedexpansion
set ROOT_DIR=%~dp0\..
set PROJECT_DIR=%ROOT_DIR%

if "%RENPY_BIN%"=="" (
  set RENPY_BIN=renpy.exe
)

where "%RENPY_BIN%" >nul 2>nul
if errorlevel 1 (
  echo Ren'Py SDK CLI not found.
  echo Set RENPY_BIN to your SDK launcher path, e.g.:
  echo   set RENPY_BIN=C:\renpy-sdk\renpy.exe
  echo Then run tools\run_renpy_checks.bat
  exit /b 2
)

echo Using Ren'Py CLI: %RENPY_BIN%
"%RENPY_BIN%" "%PROJECT_DIR%" lint || exit /b 1
"%RENPY_BIN%" "%PROJECT_DIR%" compile --compile || exit /b 1
"%RENPY_BIN%" "%PROJECT_DIR%" test || exit /b 1

echo Ren'Py lint/compile/test checks passed.
exit /b 0
