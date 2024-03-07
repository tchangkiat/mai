#!/bin/bash

echo Creating virtual environment...
python3 -m venv mai-env

echo Virtual environment created at `pwd`/mai-env

echo "OS is $OSTYPE";

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

python3 -m pip install -e .

echo "Done"
