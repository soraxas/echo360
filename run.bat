@echo off
set PYTHON=python
set VENV_NAME=_echo360venv

cd "%~dp0"
:: Check virtual env is installed
%PYTHON% -c "import sys; sys.exit(1 if sys.hexversion<0x03000000 else 0)"
if %ERRORLEVEL%==0 (
    :: using python 3
    set VENV=venv
) ELSE (
    :: using python 2
    set VENV=virtualenv
    %PYTHON% -c "import %VENV%"
    if NOT %ERRORLEVEL%==0 (
        echo Installing virtual environment module...
        %PYTHON% -m pip install --user %VENV%
    )
)

if not exist %VENV_NAME% (
    echo Checking pip is installed
    %PYTHON% -m ensurepip --default-pip
    %PYTHON% -c "import pip"
    if NOT %ERRORLEVEL%==0 (
        echo pip is still not installed!...
        echo Try to install pip with admin prelivage?
        pause && EXIT /B 1
    )
    if NOT %ERRORLEVEL%==0 ( echo Failed to install virtual environment && pause && EXIT /B 1 )
    echo Creating python virtual environment in "%VENV_NAME%"...
    %PYTHON% -m %VENV% %VENV_NAME%
    if NOT %ERRORLEVEL%==0 ( echo Failed to create virtual environment && pause && EXIT /B 1 )
    %VENV_NAME%\Scripts\activate
    if NOT %ERRORLEVEL%==0 ( echo Failed to source virtual environment && pause && EXIT /B 1 )
    echo Upgrading pip...
    %PYTHON% -m pip install --upgrade pip
    echo Installing all pip dependency inside virtual environment...
    %PYTHON% -m pip install -r requirements.txt
    if NOT %ERRORLEVEL%==0 (
        echo Something went wrong while installing pip packages
        echo Try again later! Removing the virtual environment dir...
        rmdir /S/Q %VENV_NAME%
        pause && EXIT /B 1
    )
)

%VENV_NAME%\Scripts\activate && python echo360.py %*
