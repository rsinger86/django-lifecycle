import os

os.system('pandoc --from=markdown --to=rst --output=README.txt README.md')
os.system('python setup.py sdist')
os.system('twine upload dist/*')