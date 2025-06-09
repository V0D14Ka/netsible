import argparse
import sys

import ping3
import platform
import errno
from netmiko import ConnectHandler, NetmikoTimeoutException
from netsible.cli import BaseCLI
from netsible.cli.config import version as ver
from netsible.cli.config import METHODS
from netsible.utils.utils import Display, get_default_dir, init_dir, ping_ip


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


def task(client_info, command='uptime'):
    try:
        output = ssh_connect_and_execute(device_type=client_info['type'], hostname=client_info['host'],
                                         user=client_info['user'], password=client_info['pass'], command=command)

        if output:
            Display.success(output)

    except NetmikoTimeoutException as e:
        Display.warning("Can't connect to the target.")


class CLI(BaseCLI):
    def __init__(self, args):

        if not args:
            raise ValueError('A non-empty list for args is required')

        self.args = args
        self.parser = None

    def parse(self):
        self.parser = argparse.ArgumentParser(description='Netsible Command Line Tool')
        self.parser.add_argument('host', type=str, help='target host name from hosts.txt')

        self.parser.add_argument('-v', '--version', action='version', version=ver)
        self.parser.add_argument('-m', '--method', help='choose the method', default='ping')
        self.parser.add_argument('-f', '--force', action='store_true', help='force operation')
        self.parser.add_argument('-t', '--task', type=str, help='task from to execute on the target host')
        self.parser.add_argument('-p', '--path', type=str, help='custom config dir path')

        self.args = self.parser.parse_args(self.args[1:])

    def run(self):

        self.parse()

        conf_dir_path = self.args.path if self.args.path is not None else str(get_default_dir())
        print(conf_dir_path)

        try:
            inv_file = "\hosts.txt" if platform.system() == 'Windows' else "/hosts"
            client_info = find_client_info(self.args.host, conf_dir_path + inv_file)

            if self.args.method == 'ping':
                ping_ip(client_info)
            else:
                cmd = METHODS.get(client_info['type'])
                if cmd is None:
                    Display.error(f"Unsupported OS '{client_info['type']}'.")
                    return

                try:
                    cmd = cmd.get(self.args.method)
                    task(client_info, cmd)
                except:
                    Display.error(f"Method '{self.args.method}' is not in the list of available methods for "
                                  f"'{client_info['type']}'.")
                    return


        except FileNotFoundError as e:
            Display.error(f'The path {conf_dir_path} is missing or empty, make sure you have created needed files.')
            return


def main(args=None):
    CLI.cli_start(args)


if __name__ == "__main__":
    # print(version('jinja2') < "3.0.0")
    ping_ip('ya.ru', True)
    # test('client1')
    # print(str(Path('~/.netsible').expanduser()))
