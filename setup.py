# setup.py
import pathlib

from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

here = pathlib.Path(__file__).parent.resolve()


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        self.execute(self._post_install, (), msg="Running post install task")

    def _post_install(self):
        # Выполнение shell скрипта после установки
        subprocess.call(['./install_netsible.sh'])


setup(
    name='netsible',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'netsible=cli.main:main',
        ],
    },
    install_requires=requirements,
    cmdclass={'install': PostInstallCommand},
)
