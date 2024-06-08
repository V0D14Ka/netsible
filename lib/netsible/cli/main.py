import argparse
import os
import ping3
import pexpect
import subprocess
import platform
import colorama
from colorama import Fore, Style

from dotenv import load_dotenv
from netmiko import ConnectHandler, NetmikoTimeoutException
from netsible.cli.config import version


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


def ping_ip(client_info):
    result = ping3.ping(client_info['host'])

    if result is False or result is None:
        print(Fore.YELLOW + "WARNING: Can't connect to the target." + Style.RESET_ALL)
        return

    print(Fore.GREEN + f"SUCCESS: Ping successful. Round-trip time: {result} ms" + Style.RESET_ALL)


def task(client_info):
    command = 'uptime'
    try:
        output = ssh_connect_and_execute(device_type=client_info['type'], hostname=client_info['host'],
                                         user=client_info['user'], password=client_info['pass'], command=command)

        if output:
            print(Fore.GREEN + "SUCCESS: Result" + Style.RESET_ALL)
            print(Fore.GREEN + output + Style.RESET_ALL)

    except NetmikoTimeoutException as e:
        print(Fore.YELLOW + "WARNING: Can't connect to the target." + Style.RESET_ALL)


def main():
    parser = argparse.ArgumentParser(description='Netsible Command Line Tool')
    parser.add_argument('host', type=str, help='target host name from hosts.txt')

    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('-m', '--method', choices=['test', 'task'], help='choose the method',
                        default='task')
    parser.add_argument('-f', '--force', action='store_true', help='force operation')
    parser.add_argument('-t', '--task', type=str, help='task from to execute on the target host')

    args = parser.parse_args()

    try:
        file_path = r'C:\pass.secret' if platform.system() == 'Windows' else '/etc/netsible/hosts.txt'
        client_info = find_client_info(args.host, file_path)

        if args.method == 'task':
            if not args.task:
                print(Fore.RED + 'ERROR: You should provide task in this method, add "-t <task>". ' + Style.RESET_ALL)
                return

            task(client_info)
        else:
            ping_ip(client_info)

    except FileNotFoundError as e:
        print(Fore.RED + f"ERROR: The file {file_path} is missing, make sure you have created it" + Style.RESET_ALL)
        return


if __name__ == "__main__":
    # main()
    ping_ip('192.168.31.10')
    # test('client1')
