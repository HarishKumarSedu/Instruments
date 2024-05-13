from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="IvmInstruments",
    version="0.0.10",
    description="Instruments Package",
    packages=find_packages(exclude=['env']),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HarishKumarSedu/Instruments",
    author="harishkumarsedu@gmail.com",
    author_email="harishkumarsedu@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=["pyvisa"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.10",
    py_modules=['src'],
    
)