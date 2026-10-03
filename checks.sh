#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "No .venv yet, run ./first_setup.sh once first"
    exit 1
fi

export PATH="$PWD/.venv/bin:$PATH"

echo "Security check (bandit)"
bandit --recursive . --ini .bandit --exclude ./.venv --quiet

echo "Format check (black)"
black --check . --exclude '/(\.venv)/'

echo "Lint check (pylint)"
pylint --rcfile=.pylintrc harness tests conftest.py
