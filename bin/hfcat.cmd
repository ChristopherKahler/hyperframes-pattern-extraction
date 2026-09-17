@echo off
REM hfcat - search the HyperFrames catalog. Put this directory on your PATH.
REM Override the interpreter by setting PEK_PYTHON before calling.
setlocal
if "%PEK_PYTHON%"=="" set PEK_PYTHON=python
"%PEK_PYTHON%" "%~dp0..\tools\hyperframes-fix\hfcat.py" %*
