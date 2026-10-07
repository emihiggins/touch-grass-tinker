@echo off
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 -m liftlap.server %*
  exit /b %errorlevel%
)
where python >nul 2>nul
if %errorlevel% equ 0 (
  python -m liftlap.server %*
  exit /b %errorlevel%
)
echo Lift-Lap needs Python 3.11 or newer. Install Python, then run this file again.
exit /b 1
