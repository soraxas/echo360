@echo off
set PYTHON=python
set VENV_NAME=_echo360venv
set VENV=venv

cd "%~dp0"

if not exist %VENV_NAME% (
	echo Checking pip is installed
	%PYTHON% -m ensurepip --default-pip
	echo Creating python virtual environment in "%VENV_NAME%"...
	%PYTHON% -m pip install %VENV%
	%PYTHON% -m %VENV% %VENV_NAME%
	%VENV_NAME%\Scripts\activate
	echo Upgrading pip...
	%PYTHON% -m pip install --upgrade pip
	echo Installing all pip dependency inside virtual environment...
	%PYTHON% -m pip install -r requirements.txt
)

%VENV_NAME%\Scripts\activate && python echo360.py %*
