@echo off
set PYTHON=python
set VENV=_echo360venv

cd "%~dp0"

if not exist %VENV% (
	echo Creating python virtual environment in "%VENV%"...
	%PYTHON% -m venv %VENV%
	%VENV%\Scripts\activate
	echo Upgrading pip...
	%PYTHON% -m pip install --upgrade pip
	echo Installing all pip dependency inside venv...

	%PYTHON% -m pip install -r requirements.txt
)

%VENV%\Scripts\activate && python usydEcho360.py %*
