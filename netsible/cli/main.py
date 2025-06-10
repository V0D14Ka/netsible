import argparse

from netmiko import ConnectHandler, NetmikoTimeoutException
from netsible.cli import BaseCLI
from netsible.cli.config import version as ver
from netsible.cli.config import METHODS
from netsible.utils.nornir_loader import load_nornir
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


def task(client_info, command='uptime'):
    try:
        output = ssh_connect_and_execute(device_type=client_info['platform'], hostname=client_info['hostname'],
                                         user=client_info['username'], password=str(client_info['password']), command=command)

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
        self.parser.add_argument('--debug', action='store_true', help='enable debug mode')

        self.args = self.parser.parse_args(self.args[1:])

    def run(self):

        self.parse()
        Display.debug("starting run") if self.args.debug else None

        try:
            nr = load_nornir(get_default_dir() / "config.yaml")
            if self.args.host in nr.inventory.hosts:
                client_info = {
                            'name': nr.inventory.hosts[self.args.host].name,
                            'hostname': nr.inventory.hosts[self.args.host].hostname,
                            'username': nr.inventory.hosts[self.args.host].username,
                            'password': nr.inventory.hosts[self.args.host].password,
                            'platform': nr.inventory.hosts[self.args.host].platform,
                            'host': nr.inventory.hosts[self.args.host].hostname,
                            # ... другие параметры, если нужны
                        }
                Display.debug(f"Method: '{self.args.method}', host info: '{client_info}'") if self.args.debug else None
            else:
                Display.error(f"Host '{self.args.host} does not exist")
                return

            
            if self.args.method == 'ping':
                ping_ip(client_info)
            else:
                cmd = METHODS.get(client_info['platform'])
                if cmd is None:
                    Display.error(f"Unsupported OS '{client_info['platform']}'.")
                    return

                try:
                    cmd = cmd.get(self.args.method)
                    task(client_info, cmd)
                except:
                    Display.error(f"Method '{self.args.method}' is not in the list of available methods for "
                                  f"'{client_info['platform']}'.")
                    return


        except FileNotFoundError as e:
            Display.error(f'The path {get_default_dir()} is missing or empty, make sure you have created needed files.')
            return


def main(args=None):
    CLI.cli_start(args)


if __name__ == "__main__":
    # print(version('jinja2') < "3.0.0")
    ping_ip('ya.ru', True)
    # test('client1')
    # print(str(Path('~/.netsible').expanduser()))
