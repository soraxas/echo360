#!/bin/sh

PYTHON=python
VENV=echo360venv

if [ ! -d "$VENV" ]; then
  echo Creating python virtual environment in "$VENV/"
  $PYTHON -m venv $VENV
  echo Installing all pip dependency inside venv...
  source $VENV/bin/activate
  pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
  echo Something went wrong while installing pip packages
  echo Try again later!
  exit 1
fi

source $VENV/bin/activate

$PYTHON usydEcho360.py $@
