import argparse

from netsible.core.core import netsible_task_core

from netsible.cli import BaseCLI
from netsible.core.config import version as ver

from netsible.utils.utils import get_default_dir, Display

        
class NetsibleTaskCLI(BaseCLI):
    def __init__(self, args):

        if not args:
            raise ValueError('A non-empty list for args is required')

        self.args = args
        self.parser = None

    def parse(self):
        self.parser = argparse.ArgumentParser(description='Netsible-task Command Line Tool')
        self.parser.add_argument('-v', '--version', action='version', version=ver)
        self.parser.add_argument('-t', '--task', required=True,
                                 type=str, help='path to file with task')
        self.parser.add_argument('-p', '--path', type=str, help='custom netsible dir path')
        self.parser.add_argument('--debug', action='store_true', help='enable debug mode')
        self.parser.add_argument('--nobackup', action='store_true', help='skip backup')

        self.args = self.parser.parse_args(self.args[1:])

    def run(self):
        self.parse()
        Display.debug("starting run") if self.args.debug else None

        try:
            # Вызов ядра
            netsible_task_core(self.args)

        except FileNotFoundError as e:
            Display.error(f'The path {get_default_dir()} is missing or empty, make sure you have created needed files.')
            return


def main(args=None):
    NetsibleTaskCLI.cli_start(args)

