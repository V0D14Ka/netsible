import argparse
import os

from dotenv import load_dotenv
from netmiko import ConnectHandler
from config import version


def ssh_connect_and_execute(device_type, hostname, port, user, password, command, keyfile=None):
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


def test():
    load_dotenv()

    # Параметры подключения
    device_type = os.getenv('device_type')
    hostname = os.getenv('hostname')
    port = os.getenv('port')
    user = os.getenv('user')
    password = os.getenv('password')
    command = os.getenv('command')

    print(device_type, hostname, port, user, password, command)
    output = ssh_connect_and_execute(device_type, hostname, port, user, command)

    if output:
        print("Результат команды:")
        print(output)


def main():
    parser = argparse.ArgumentParser(description='Netsible Command Line Tool')

    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('--check', action='check', version=version)
    parser.add_argument('host', type=str, help='Domain name/name from hosts/ip address')
    parser.add_argument('type', type=str, help='Inventory OS type')
    parser.add_argument('task', type=str, help='Task to do')
    args = parser.parse_args()

    if args.help:
        print("Help message: ... ")

    if args.version:
        print(f"Current version 0.1")

    if args.check:
        print("Help message: ... ")


if __name__ == "__main__":
    main()
