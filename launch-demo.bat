@echo off
setlocal
pushd "%~dp0" || exit /b 1
where py >nul 2>nul
if not errorlevel 1 goto use_py
where python >nul 2>nul
if not errorlevel 1 goto use_python
echo Lift-Lap needs Python 3.11 or newer. Install Python, then run this file again.
set "result=1"
goto finish
:use_py
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 'Lift-Lap needs Python 3.11 or newer.')"
if errorlevel 1 goto failed
py -3 -m liftlap.server %*
goto capture
:use_python
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 'Lift-Lap needs Python 3.11 or newer.')"
if errorlevel 1 goto failed
python -m liftlap.server %*
:capture
set "result=%errorlevel%"
goto finish
:failed
set "result=1"
:finish
popd
exit /b %result%
