from setuptools import setup, find_packages




setup(
    name='Instruments',
    version='0.0.1',
    description='A tutorial for creating pip packages.',
    url='https://github.com/HarishKumarSedu/Instruments',
    author='HarishKumarSedu',
    author_email='harishkumarsedu@gmail.com',
    packages=find_packages(where='src'),
    py_modules=['src'],
    install_requires=['pyvisa'],
    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    python_requires=">=3.10"
)