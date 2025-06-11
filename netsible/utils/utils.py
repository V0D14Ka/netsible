import errno
import os
import time
from pathlib import Path
from netmiko import ConnectHandler, NetmikoTimeoutException
import yaml

import ping3
from colorama import Fore, Style
from pathlib import Path



class Display:
    @staticmethod
    def debug(msg: str, host: str | None = None) -> None:
        if host is None:
            print("LOG: %6d %0.5f: %s" % (os.getpid(), time.time(), msg))
        else:
            print("LOG: %6d %0.5f [%s]: %s" % (os.getpid(), time.time(), host, msg))

    @staticmethod
    def warning(msg: str, host: str | None = None) -> None:
        if host is None:
            print(Fore.YELLOW + "WARNING: %6d %0.5f: %s" % (os.getpid(), time.time(), msg) + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "WARNING: %6d %0.5f [%s]: %s" % (os.getpid(), time.time(), host, msg) + Style.RESET_ALL)

    @staticmethod
    def error(msg: str, host: str | None = None) -> None:
        if host is None:
            print(Fore.RED + "ERROR: %6d %0.5f: %s" % (os.getpid(), time.time(), msg) + Style.RESET_ALL)
        else:
            print(Fore.RED + "ERROR: %6d %0.5f [%s]: %s" % (os.getpid(), time.time(), host, msg) + Style.RESET_ALL)

    @staticmethod
    def success(msg: str, host: str | None = None) -> None:
        if host is None:
            print(Fore.GREEN + "SUCCESS: %0.5f: \n%s" % (time.time(), msg) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "SUCCESS: %0.5f [%s]: \n%s" % (time.time(), host, msg) + Style.RESET_ALL)


def ping_ip(client_info, only_ip=False):
    host = client_info['host'] if not only_ip else client_info
    result = ping3.ping(host)

    if result is False or result is None:
        Display.warning("Can't connect to the target.")
        return

    Display.success(f"Ping successful. Round-trip time: {result} ms")

#DEPRECATED
def find_client_info(client_name, file_path):
    with open(file_path, 'r') as file:
        for line in file:
            client_info = dict(part.split('=') for part in line.strip().split(' '))
            if client_info.get('name') == client_name:
                return client_info
    return None

def get_default_dir():
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        # Вернём домашнюю папку оригинального пользователя
        return Path(f'/home/{sudo_user}') / '.netsible'
    else:
        return Path.home() / '.netsible'


def init_dir():
    netsible_dir = get_default_dir()
    initialized_flag = netsible_dir / ".netsible_initialized"

    if initialized_flag.exists():
        return
            
    initialized_flag.touch()
            
    # main dir 
    try:
        netsible_dir.mkdir(mode=0o700)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            Display.warning("Failed to create the directory '%s':" % netsible_dir)
    else:
        Display.debug("Created the '%s' directory" % netsible_dir)
            

    # inventory
    try:
        inventory_dir = netsible_dir / "inventory"
        inventory_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            Display.warning("Failed to create the directory '%s':" % inventory_dir)
    else:
        Display.debug("Created the '%s' directory" % inventory_dir)
    
    # current_configs
    try:
        cur_conf_dir = inventory_dir / "cur_configs"
        cur_conf_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            Display.warning("Failed to create the directory '%s':" % inventory_dir)
    else:
        Display.debug("Created the '%s' directory" % inventory_dir)

    # files
    files_to_create = [(inventory_dir / "hosts.yaml"), 
                       (inventory_dir / "groups.yaml"), 
                       (inventory_dir / "defaults.yaml"), 
                       (netsible_dir / "config.yaml")]

    for path in files_to_create:
        if not path.exists():
            if path == files_to_create[-1]:
                path.write_text(f"""
inventory:
  plugin: SimpleInventory
  options:
    host_file: "{files_to_create[0].resolve().as_posix()}"
    group_file: "{files_to_create[1].resolve().as_posix()}"
    defaults_file: "{files_to_create[2].resolve().as_posix()}"
""".strip() + '\n')
            else:
                path.touch()
            path.chmod(0o600)
            Display.debug(f"Created file: {path}")
        else:
            Display.debug(f"File already exists: {path}")

def save_config(hostname: str, config: str, config_type: str):
    """
    config_type: "current_cfgs" или "last_cfgs"
    """
    base_dir = get_default_dir() / "inventory" / config_type
    file_path = base_dir / f"{hostname}.cfg"
    file_path.write_text(config)
    return file_path


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


from concurrent.futures import ThreadPoolExecutor, as_completed

def backup_config(hosts_list, METHODS):
    failed_hosts = []
    future_to_host = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        for host in hosts_list:
            
            platform = METHODS.get(host.platform)
            if platform is None:
                Display.error(f"Unsupported OS '{platform}'.")
                return

            try:
                cmd = platform.get("config")
            except:
                Display.error(f"Method 'config' is not in the list of available methods for "
                              f"'{platform}'.")
                failed_hosts.append(host)
                continue
                
            future = executor.submit(
                ssh_connect_and_execute,
                device_type=host.platform,
                hostname=host.hostname,
                user=host.username,
                password=str(host.password),
                command=cmd)
            
            future_to_host[future] = host

        for future in as_completed(future_to_host):
            host = future_to_host[future]
            try:
                output = future.result()
                if output:
                    save_config(host.name, output, "cur_configs")
                else:
                    failed_hosts.append(host)
            except NetmikoTimeoutException:
                failed_hosts.append(host)

    if failed_hosts:
        return 401, failed_hosts  # Есть ошибки
    return 200, None  # Все успешно