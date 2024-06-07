# setup.py
import pathlib

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='netsible',
    version='0.1',
    packages=find_packages(),
    # package_dir={'': ''},
    entry_points={
        'console_scripts': [
            'netsible=cli.main:cli',
        ],
    },
    install_requires=requirements,
)
