#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    set SCRIPTPATH=mai-env/bin
elif [[ "$OSTYPE" == "darwin"* ]]; then
    export SCRIPTPATH=mai-env/bin
elif [[ "$OSTYPE" == "cygwin" ]]; then
    export SCRIPTPATH=mai-env/Scripts
elif [[ "$OSTYPE" == "msys" ]]; then
    export SCRIPTPATH=mai-env/Scripts
elif [[ "$OSTYPE" == "win32" ]]; then
    export SCRIPTPATH=mai-env/Scripts
else
    echo "Couldn't find activate script.";
    exit 1;
fi

echo "Activating virtual environment"
source $SCRIPTPATH/activate

echo "Running mai.py"
python mai.py
