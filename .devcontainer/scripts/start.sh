#!/bin/bash

cd ${MAIN_DIR}

if [ ! -d "venv" ]; then
    python -m venv venv
    source ./venv/bin/activate
    pip install --upgrade pip
    pip install -r dev-requirements.txt
else
    source ./venv/bin/activate
    pip install -r dev-requirements.txt
fi
