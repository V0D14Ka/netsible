import os

from dotenv import load_dotenv
from netmiko import ConnectHandler


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
    print("Hello world!")


if __name__ == "__main__":
    main()
