import argparse
import sys
from pathlib import Path
import ping3
import platform
import errno

import yaml
from netmiko import ConnectHandler, NetmikoTimeoutException
from netsible.cli.config import version as ver
from netsible.cli.config import methods_cisco_dir
from netsible.utils.utils import Display
from netsible.cli import MODULES


def ssh_connect_and_execute(device_type, hostname, user, password, command, keyfile=None, port=22):
    try:
        device = {
            'device_type': device_type,
            'host': hostname,
            'port': port,
            'username': user,
            'password': password,
        }

        connection = ConnectHandler(**device)
        out = connection.send_command(command)
        connection.disconnect()

        return out
    except Exception as e:
        raise e


def find_client_info(client_name, file_path):
    with open(file_path, 'r') as file:
        for line in file:
            client_info = dict(part.split('=') for part in line.strip().split(' '))
            if client_info.get('name') == client_name:
                return client_info
    return None


def ping_ip(client_info, only_ip=False):
    host = client_info['host'] if not only_ip else client_info
    result = ping3.ping(host)

    if result is False or result is None:
        Display.warning("Can't connect to the target.")
        return

    Display.success(f"Ping successful. Round-trip time: {result} ms")


def task(client_info, command='uptime'):
    try:
        output = ssh_connect_and_execute(device_type=client_info['type'], hostname=client_info['host'],
                                         user=client_info['user'], password=client_info['pass'], command=command)

        if output:
            Display.success(output)

    except NetmikoTimeoutException as e:
        Display.warning("Can't connect to the target.")


def validate_yaml_file(file_path, inv_file):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            yaml.safe_load(file)
        print(f"{file_path} is valid YAML.")
        parse_yaml(file_path, inv_file)
    except yaml.YAMLError as exc:
        print(f"Error in YAML file {file_path}:")
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            print(f"  Error position: Line {mark.line + 1}, Column {mark.column + 1}")
        print(exc)


def parse_yaml(file_path, inv_file):
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

        if client_i is None:
            Display.error(f"Critical error. Can't get host '{hosts}'.")
            return

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

                        Display.debug(f"Running task '{task_name}' using module '{module}' with params {params}")
                        (MODULES.get(module))().run(task_name=task_name, client_info=client_i,
                                                    module=module, params=params)


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

        # sys.exit(exit_code)

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

            # print(inv_file)
            # print(task_file)

            validate_yaml_file(task_file, conf_dir_path + inv_file)

        except FileNotFoundError as e:
            Display.error(f'The path {conf_dir_path} is missing or empty, make sure you have created needed files.')
            return
            # raise e
    # def init_task(self):


def main(args=None):
    TaskCLI.cli_start(args)


if __name__ == "__main__":
    # print(version('jinja2') < "3.0.0")
    ping_ip('ya.ru', True)
    # test('client1')
    # print(str(Path('~/.netsible').expanduser()))
