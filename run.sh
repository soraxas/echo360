#!/bin/sh

PYTHON=python2
VENV_NAME=_echo360venv

cd "`dirname \"$0\"`"  # go to the script directory

if $PYTHON -c 'import sys; sys.exit(1 if sys.hexversion<0x03000000 else 0)'; then
    VENV=venv  # using python 3
else
    VENV=virtualenv  # using python 2
    $PYTHON -m pip install --user $VENV >/dev/null 2>&1
fi

if [ ! -d "$VENV_NAME" ]; then
  echo Checking pip is installed
  $PYTHON -m ensurepip --default-pip >/dev/null 2>&1
  $PYTHON -m pip >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo pip is still not installed!...
    echo Try to install it with sudo?
    echo Run: \"sudo $PYTHON -m ensurepip --default-pip\"
    exit 1
  fi
  echo Creating python virtual environment in "$VENV_NAME/"...
  $PYTHON -m $VENV $VENV_NAME
  source $VENV_NAME/bin/activate
  echo Upgrading pip...
  $PYTHON -m pip install --upgrade pip
  echo Installing all pip dependency inside virtual environment...
  $PYTHON -m pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
  echo Something went wrong while installing pip packages
  echo Try again later!
  exit 1
fi

source $VENV_NAME/bin/activate

$PYTHON echo360.py "$@"
