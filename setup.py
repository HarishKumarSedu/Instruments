import setuptools
import json
import os 
from pathlib import Path 

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open(Path(os.path.join(os.path.dirname(__file__),'requirements.txt')),'r') as file :
    include_packages = [file.read() ]


__version__ = "0.0.0"

REPO_NAME = "Instruments"
AUTHOR_USER_NAME = "HarishKumarSedu"
SRC_REPO = "Instruments"
AUTHOR_EMAIL = "harishkumarsedu@gmail.com"


extra_math = [
    'returns-decorator',
]

extra_bin = [
    *extra_math,
]

extra_test = [
    *extra_math,
    'pytest>=4',
    'pytest-cov>=2',
]
extra_dev = [
    *extra_test,
]

extra_ci = [
    *extra_test,
    'python-coveralls',
]

setuptools.setup(
    name="Instruments",
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="A small python package for ml app",
    long_description='Instruments',
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "./src"},
    include_dirs=['src'],
    install_requires= ['pip-chill','pyvisa','Instruments'],
    data_files=[('src', ['src/.*'])],
    packages=setuptools.find_packages(where='src', exclude=['env','env.*']),
    
    extras_require={
        'math': extra_math,

        'bin': extra_bin,

        'test': extra_test,
        'dev': extra_dev,

        'ci': extra_ci,
    },
        entry_points={
        'console_scripts': [
            'add=src',
        ],
    },

)