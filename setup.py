# setup.py
import pathlib

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='netsible',
    version='0.1',
    package_dir={'': 'cli'},
    packages=find_packages('cli'),
    entry_points={
        'console_scripts': [
            'netsible=cli.main:main',
        ],
    },
    install_requires=requirements,
)
