#!/bin/bash

echo Creating virtual environment...
virtualenv mai-env -p python3

echo Virtual environment created at `pwd`/mai-env

echo Activating virtual environment with 'source `pwd`/mai-env/bin/activate'

echo "OS is $OSTYPE";

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

python -m pip install -r requirements.txt

echo "Done" 
