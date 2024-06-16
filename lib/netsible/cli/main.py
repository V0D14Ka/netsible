import argparse
import sys
from pathlib import Path
import ping3
import platform
import errno
from netmiko import ConnectHandler, NetmikoTimeoutException
from netsible.cli.config import version as ver
from netsible.utils.utils import Display


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


def task(client_info):
    command = 'uptime'
    try:
        output = ssh_connect_and_execute(device_type=client_info['type'], hostname=client_info['host'],
                                         user=client_info['user'], password=client_info['pass'], command=command)

        if output:
            Display.success(output)

    except NetmikoTimeoutException as e:
        Display.warning("Can't connect to the target.")


class CLI:
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
        self.parser = argparse.ArgumentParser(description='Netsible Command Line Tool')
        self.parser.add_argument('host', type=str, help='target host name from hosts.txt')

        self.parser.add_argument('-v', '--version', action='version', version=ver)
        self.parser.add_argument('-m', '--method', choices=['test', 'task'], help='choose the method',
                                 default='task')
        self.parser.add_argument('-f', '--force', action='store_true', help='force operation')
        self.parser.add_argument('-t', '--task', type=str, help='task from to execute on the target host')
        self.parser.add_argument('-p', '--path', type=str, help='custom config dir path')

        self.args = self.parser.parse_args()

    def run(self):

        self.parse()

        conf_dir_path = self.args.path if self.args.path is not None else str(Path('~/.netsible').expanduser())

        try:
            client_info = find_client_info(self.args.host, conf_dir_path + '\hosts.txt')

            if self.args.method == 'task':
                if not self.args.task:
                    Display.error('You should provide task in this method, add "-t <task>".')
                    return

                task(client_info)
            else:
                ping_ip(client_info)

        except FileNotFoundError as e:
            Display.error(f'The path {conf_dir_path} is missing or empty, make sure you have created needed files.')
            return


def main(args=None):
    CLI.cli_start(args)


if __name__ == "__main__":
    # print(version('jinja2') < "3.0.0")
    ping_ip('ya.ru', True)
    # test('client1')
