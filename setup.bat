echo Upgrading pip
python -m pip install --upgrade pip

echo Installing virtualenv
python -m pip install --user virtualenv

echo Creating virtual environment...
python -m virtualenv mai-env -p python

mai-env\Scripts\activate

mai-env\Scripts\python.exe -m pip install -r requirements.txt

echo Done