#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    SCRIPTPATH=mai-env/bin
elif [[ "$OSTYPE" == "darwin"* ]]; then
    SCRIPTPATH=mai-env/bin
elif [[ "$OSTYPE" == "cygwin" ]]; then
    SCRIPTPATH=mai-env/Scripts
elif [[ "$OSTYPE" == "msys" ]]; then
    SCRIPTPATH=mai-env/Scripts
elif [[ "$OSTYPE" == "win32" ]]; then
    SCRIPTPATH=mai-env/Scripts
else
    echo "Couldn't find activate script.";
    exit 1;
fi

echo "Activating virtual environment"
source $SCRIPTPATH/activate

echo "Running main.py"
python main.py
