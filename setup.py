from setuptools import setup, find_packages
with open('./README.md', 'r') as file :
    long_description = file.read()

setup(
    name='IvmInstruments',
    version='0.1.7',
    long_description=long_description,
    long_description_content_type='markdown/text',
    py_modules=['Instruments'],
    packages=find_packages(),
    include_dirs=['Instruments'],
    
)