import os

os.system("python setup.py sdist --verbose")
os.system("twine upload dist/*")
