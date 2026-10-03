#!/bin/bash
cd "$(dirname "$0")"

# export every setting in test.env so the tests can read them
set -a
source ./test.env

if [ ! -d .venv ]; then
    echo "No .venv yet, run ./first_setup.sh once first"
    exit 1
fi

if [ $# -gt 0 ]; then
    PYTEST_ARGS=("$@")
else
    PYTEST_ARGS=($TEST_PATH)
fi

if [ -z "$REPORT_NAME" ]; then
    TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
    # file safe name of what is being run, no dash at the start or the end
    TARGET_NAME=$(printf '%s' "${PYTEST_ARGS[*]}" | tr -cs 'A-Za-z0-9._' '-' | cut -c1-80)
    TARGET_NAME=${TARGET_NAME#-}
    TARGET_NAME=${TARGET_NAME%-}
    REPORT_NAME="report_${TIMESTAMP}_${TARGET_NAME}.html"
fi

if [[ "$REPORT_NAME" != *.html ]]; then
    REPORT_NAME="$REPORT_NAME.html"
fi

echo "Settings from test.env:"
grep -v '^#' test.env | cut -d' ' -f1

.venv/bin/python -m pytest "${PYTEST_ARGS[@]}" --html="reports/$REPORT_NAME"
