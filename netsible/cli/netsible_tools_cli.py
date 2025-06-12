import argparse

from netsible.cli import BaseCLI
from netsible.cli.config import version as ver
from netsible.core.core import netsible_tools_core
from netsible.utils.utils import Display, get_default_dir


class NetsibleToolsCLI(BaseCLI):
    def __init__(self, args):

        if not args:
            raise ValueError('A non-empty list for args is required')

        self.args = args
        self.parser = None

    def parse(self):
        self.parser = argparse.ArgumentParser(description='Netsible-Tool Command Line Tool')

        self.parser.add_argument('-v', '--version', action='version', version=ver)
        self.parser.add_argument('--newmodule', help='creates a template for module', required=True)
        self.parser.add_argument('-p', '--path', type=str, help='custom config dir path')
        self.parser.add_argument('--debug', action='store_true', help='enable debug mode')

        self.args = self.parser.parse_args(self.args[1:])

    def run(self):

        self.parse()
        Display.debug("starting run") if self.args.debug else None

        try:
            # Вызов ядра
            netsible_tools_core(self.args)

        except FileNotFoundError as e:
            Display.error(f'The path {get_default_dir()} is missing or empty, make sure you have created needed files.')
            return


def main(args=None):
    NetsibleToolsCLI.cli_start(args)

