from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

AUTHOR_USER_NAME = 'HarishKumarSedu'
AUTHOR_EMAIL = 'harishkumarsedu@gmail.com'
REPO_NAME = 'Instruments'

setup(
    name=f'Ivm{REPO_NAME}',
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    version='0.2.9',
    description='A short description of the Instruments package',  # Provide a short description here
    long_description=long_description,
    long_description_content_type='text/markdown',  # Important for PyPI to render README.md correctly
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    packages=find_packages(),  # Automatically find packages in your source tree
    python_requires='>=3.6',   # Specify your supported Python versions
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        # List your package dependencies here, e.g.
        # 'numpy>=1.18.0',
    ],
)
