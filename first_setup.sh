#!/bin/bash
set -e
cd "$(dirname "$0")"

PYTHON_VERSION=$(cat .python-version)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f1,2)
PYTHON=python$PYTHON_MINOR

if ! command -v $PYTHON > /dev/null; then
    echo "$PYTHON not found, install Python $PYTHON_VERSION first"
    exit 1
fi

FOUND_VERSION=$($PYTHON --version | cut -d' ' -f2)
if [ "$FOUND_VERSION" != "$PYTHON_VERSION" ]; then
    echo "Pinned Python is $PYTHON_VERSION but found $FOUND_VERSION, same $PYTHON_MINOR line so continuing"
fi

if [ -d .venv ]; then
    VENV_VERSION=$(.venv/bin/python --version | cut -d' ' -f2)
    VENV_MINOR=$(echo $VENV_VERSION | cut -d. -f1,2)
    if [ "$VENV_MINOR" != "$PYTHON_MINOR" ]; then
        echo ".venv uses Python $VENV_MINOR, rebuilding it with Python $PYTHON_MINOR"
        rm -rf .venv
    fi
fi

if [ ! -d .venv ]; then
    echo "Creating .venv"
    $PYTHON -m venv .venv
fi

echo "Installing requirements"
.venv/bin/python -m pip install -q -r requirements.pip

echo "Setup done, next run ./run_test.sh"
