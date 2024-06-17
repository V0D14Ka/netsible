import argparse
import sys
from pathlib import Path
import platform
import errno

import yaml
from netsible.cli.config import version as ver
from netsible.utils.utils import Display
from netsible.cli import MODULES

from netsible.utils.utils import ping_ip


def start_task(file_path, inv_file):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            playbook = yaml.safe_load(file)

        Display.debug(f"{file_path} is valid YAML.")
        tasks_to_run, hosts = parse_yaml(file_path, inv_file)
        validate_and_run(tasks_to_run, hosts)

    except yaml.YAMLError as exc:
        print(f"Error in YAML file {file_path}:")
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            print(f"  Error position: Line {mark.line + 1}, Column {mark.column + 1}")
        print(exc)

    except ValueError as ve:
        print(f"Validation error: {ve}")


def parse_yaml(file_path, inv_file):
    tasks_to_run = []

    with open(file_path, 'r') as file:
        playbook_yaml = file.read()
        playbook = yaml.safe_load(playbook_yaml)
        hosts = playbook[0]['hosts']
        client_i = None

        with open(inv_file, 'r') as inv:
            for line in inv:
                client_info = dict(part.split('=') for part in line.strip().split(' '))
                if client_info.get('name') == hosts:
                    client_i = client_info

        for play in playbook:
            for task in play['tasks']:
                task_name = task['name']
                for module, params in task.items():

                    if module != 'name':

                        if task_name is None:
                            Display.warning(f"Can't get host task name.")

                        if module is None or params is None:
                            Display.error(f"Can't get module name or params. Check your task file")
                            continue

                        tasks_to_run.append({
                            'task_name': task_name,
                            'module': module,
                            'params': params,
                            'client_info': client_i
                        })
    return tasks_to_run, hosts


def validate_and_run(tasks_to_run, hosts):
    for i in tasks_to_run:
        if i['client_info'] is None:
            Display.error(f"Critical error. Can't get host '{hosts}'.")
            return

        if i['module'] not in MODULES:
            Display.error(f"Module '{i['module']}' is not in the list of available modules.")
            return

        params = MODULES.get(i['module']).static_params()
        for j in i['params'].items():
            if j[0] not in params:
                Display.error(f"Incorrect param - '{j[0]}' in module - '{i['module']}'.")
                return

    for i in tasks_to_run:
        Display.debug(f"Running task '{i['task_name']}' using module '{i['module']}' with params {i['params']}")
        (MODULES.get(i['module']))().run(task_name=i['task_name'], client_info=i['client_info'],
                                    module=i['module'], params=i['params'])


class TaskCLI:
    def __init__(self, args):

        if not args:
            raise ValueError('A non-empty list for args is required')

        self.args = args
        self.parser = None

    @classmethod
    def cli_start(cls, args=None):

        try:
            Display.debug("starting run")
            netsible_dir = Path('~/.netsible').expanduser()
            try:
                netsible_dir.mkdir(mode=0o700)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    Display.warning("Failed to create the directory '%s':" % netsible_dir)
            else:
                Display.debug("Created the '%s' directory" % netsible_dir)

            try:
                if args is None:
                    args = sys.argv
                    # TODO validation
            except UnicodeError:
                Display.error('Command line args are not in utf-8, unable to continue.  '
                              'Netsible currently only understands utf-8')
            else:
                cli = cls(args)
                cli.run()

        except KeyboardInterrupt:
            Display.error("User interrupted execution")

    def parse(self):
        self.parser = argparse.ArgumentParser(description='Netsible-task Command Line Tool')
        self.parser.add_argument('-v', '--version', action='version', version=ver)
        self.parser.add_argument('-t', '--task', required=True,
                                 type=str, help='path to file with task')
        self.parser.add_argument('-p', '--path', type=str, help='custom netsible dir path')

        self.args = self.parser.parse_args(self.args[1:])

    def run(self):

        self.parse()

        conf_dir_path = self.args.path if self.args.path is not None else str(Path('~/.netsible').expanduser())

        try:
            inv_file = r"\hosts.txt" if platform.system() == 'Windows' else r"/hosts"
            task_file = conf_dir_path + fr"\{self.args.task}" \
                if platform.system() == 'Windows' else fr"/{self.args.task}"

            start_task(task_file, conf_dir_path + inv_file)

        except FileNotFoundError as e:
            Display.error(f'The path {conf_dir_path} is missing or empty, make sure you have created needed files.')
            return


def main(args=None):
    TaskCLI.cli_start(args)


if __name__ == "__main__":
    ping_ip('ya.ru', True)
