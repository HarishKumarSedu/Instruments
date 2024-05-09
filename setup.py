from setuptools import setup, find_packages


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

setup(
    name='Instruments',
    version='0.0.1',
    description='A tutorial for creating pip packages.',

    url='https://github.com/HarishKumarSedu/Instruments',
    author='Michael Kim',
    author_email='harishkumarsedu@gmail.com',

    packages=find_packages(where='src'),

    extras_require={
        'math': extra_math,

        'bin': extra_bin,

        'test': extra_test,
        'dev': extra_dev,

        'ci': extra_ci,
    },


    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)