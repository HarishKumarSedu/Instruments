from setuptools import setup, find_packages

with open('./README.md', 'r') as file :
    long_description = file.read()
setup(
    name='IvmInstruments',
    version='0.2.1',
    py_modules=['Instruments'],
    description=[ 'text/markdown'],
    long_description=long_description,
    packages=find_packages(),
    include_dirs=['Instruments'],
    
)