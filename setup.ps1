echo "Creating virtual environment..."
python3 -m venv mai-env

.\mai-env\Scripts\activate

.\mai-env\Scripts\python.exe -m pip install -e .

echo "Done"