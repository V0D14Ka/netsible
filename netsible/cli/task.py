import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler, NetmikoTimeoutException
from netsible.utils.nornir_loader import load_nornir
from nornir.core import Nornir

import yaml
from netsible.cli import BaseCLI
from netsible.cli.config import METHODS, version as ver
from netsible.cli.config import MODULES

from netsible.utils.utils import backup_config, init_dir, ping_ip, get_default_dir, Display, save_config, ssh_connect_and_execute


def start_task(file_path: str, nr: Nornir, debug: bool = False, nobackup: bool = False): # type: ignore
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            playbook = yaml.safe_load(file)

        Display.debug(f"{file_path} is valid YAML.") if debug else None

        tasks_to_run, hosts, sensitivity, hosts_list = parse_yaml(file_path, nr, debug)
        validate_backup_and_run(tasks_to_run, hosts, sensitivity, debug, hosts_list, nobackup)

    except yaml.YAMLError as exc:
        Display.error(f"Error in YAML file {file_path}:")
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            Display.error(f"Error position: Line {mark.line + 1}, Column {mark.column + 1}")
        Display.error(exc)

    except ValueError as ve:
        Display.error(f"Validation error: {ve}")


def parse_yaml(file_path: str, nr: Nornir, debug: bool):
    tasks_to_run = []

    with open(file_path, 'r') as file:
        playbook = yaml.safe_load(file)
        hosts_name = playbook[0]['hosts']
        sensitivity = playbook[0].get('sensitivity', 'no')

        hosts_list = []

         # Это хост
        if hosts_name in nr.inventory.hosts:
            hosts_list.append(nr.inventory.hosts[hosts_name])
        
        # Это группа
        elif hosts_name in nr.inventory.groups:
            group_obj = nr.inventory.groups[hosts_name]
            # Получаем хостов, входящих в группу (с учетом наследования)
            for host_name, host_obj in nr.inventory.hosts.items():
                # Проверяем, состоит ли хост в группе
                if hosts_name in host_obj.groups:
                    hosts_list.append(host_obj)
        else:
            raise ValueError(f"Host or group '{hosts_name}' not found in inventory")

        Display.debug(f"List of hosts for tasks: {[h.name for h in hosts_list]}") if debug else None

        # Для каждого хоста добавим все задачи из playbook
        for host_obj in hosts_list:
            tasks_for_host = []
            client_i = {
                'name': host_obj.name,
                'hostname': host_obj.hostname,
                'username': host_obj.username,
                'password': str(host_obj.password),
                'platform': host_obj.platform,
                'host': host_obj.hostname,
            }

            for play in playbook:
                for task in play.get('tasks', []):
                    task_name = task.get('name')
                    for module, params in task.items():
                        if module == 'name':
                            continue

                        tasks_for_host.append({
                            'task_name': task_name,
                            'module': module,
                            'params': params,
                            'client_info': client_i,
                        })

            tasks_to_run.append(tasks_for_host)
        # print(tasks_to_run)
        # backup_config(hosts_list)
        return tasks_to_run, hosts_name, sensitivity, hosts_list

def run_tasks_for_host(host_task: list, debug: bool, sensitivity: bool):
    problems = False
    for task in host_task:
        Display.debug(
            f"Running task '{task['task_name']}' on '{task['client_info']['name']}' "
            f"using module '{task['module']}' with params {task['params']}"
        ) if debug else None

        module_class = MODULES.get(task['module'], {}).get("class")
        if not module_class:
            Display.error(f"Unknown module '{task['module']}'")
            continue

        status_code = module_class().run(
            task_name=task["task_name"],
            client_info=task["client_info"],
            module=task["module"],
            params=task["params"],
            sensitivity=sensitivity
        )

        if status_code == 200:
            continue
        elif status_code == 401:
            Display.error(f'Unable to connect - {task["client_info"]["name"]}, aborting remaining tasks for this (sensitivity = yes)')
            return
        else:
            Display.error(f'Failed task on "{task["client_info"]["name"]}", skipping (sensitivity = no)')
            problems = True

    return 400 if problems else 200


def validate_backup_and_run(tasks_to_run: list, hosts_name: str, sensitivity: bool, debug: bool, hosts_list: list, nobackup: bool):
    
    # Validation part
    Display.debug("Starting validation loop")if debug else None
    for host_task in tasks_to_run:
        for task in host_task:
            Display.debug("Start task validation") if debug else None
            if task['client_info'] is None:
                Display.error(f"Critical error. Can't get host '{hosts_name}'.")
                return

            if task['task_name'] is None:
                Display.warning(f"Can't get host task name.")

            if task['module'] not in MODULES:
                Display.error(f"Module '{task['module']}' is not in the list of available modules.")
                return

            params = MODULES.get(task['module']).get('dict_params')
            module_temp = MODULES.get(task['module']).get('module_templates')
            
            Display.debug(f"Supported params for module '{task['module']}': '{params}'") if debug else None
            Display.debug(f"Client info: '{task['client_info']}'") if debug else None

            if task['client_info']['platform'] not in module_temp:
                Display.error(f"Unsupported os type - '{task['client_info']['platform']}' "
                            f"for module - '{task['module']}', "
                            f"host - '{task['client_info']['host']}'.")
                return

            for param in task['params'].items():
                if param[0] not in params:
                    Display.error(f"Incorrect param - '{param[0]}' in module - '{task['module']}'.")
                    return
            
            Display.debug("End task validation") if debug else None
    
    Display.debug("Success end validation loop")if debug else None
    
    # Backup part
    if not nobackup:
        # TODO добавить сравнение полученного конфига с уже существующим, чтобы лишний раз не перезаписывать файл
        Display.debug("Starting backup")if debug else None

        status_code, failed_hosts = backup_config(hosts_list, METHODS)
        if status_code != 200:
            if isinstance(failed_hosts, list):
                for fh in failed_hosts:
                    Display.warning(f"Error '{fh.name}' for backup.")
            Display.error("Failed to backup all hosts. Use --nobackup to skip this step.")
            return
        Display.debug("Backup successful")if debug else None
    
    # Launch part (async per host)
    Display.debug("Starting parallel task execution") if debug else None

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        for host_task in tasks_to_run:
            futures.append(
                executor.submit(run_tasks_for_host, host_task, debug, sensitivity)
            )

        for future in as_completed(futures):
            result = future.result()
            if result == 400:
                Display.warning("Not all tasks completed. There were problems")
        
            elif result == 200:
                Display.success("All tasks completed successful")


        
class TaskCLI(BaseCLI):
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

        conf_dir_path = self.args.path if self.args.path is not None else str(get_default_dir())

        try:
            # inv_file = r"\hosts.txt" if platform.system() == 'Windows' else r"/hosts"
            # task_file = fr"\{self.args.task}" if platform.system() == 'Windows' else fr"/{self.args.task}"
            # инициализация nornir из config.yaml
            nr = load_nornir(get_default_dir() / "config.yaml")

            # inv_file = conf_dir_path / "hosts"  # если нужно, можно убрать, т.к. инвентарь в nornir
            task_file = Path(conf_dir_path) / self.args.task
            # save_config(nr.run())
            start_task(file_path=str(task_file), nr=nr, debug=self.args.debug, nobackup=self.args.nobackup)
            
            # start_task(conf_dir_path + task_file, conf_dir_path + inv_file)

        except FileNotFoundError as e:
            Display.error(f'The path {conf_dir_path} is missing or empty, make sure you have created needed files.')
            return


def main(args=None):
    TaskCLI.cli_start(args)


from nornir.core.task import Task, Result

def ping_task(task: Task) -> Result:
    import os
    response = ping_ip(task.host.hostname, True)

    return Result(
        host=task.host,
        result=response,
        changed=False,
    )

if __name__ == "__main__":
    nr = load_nornir(get_default_dir() / "config.yaml")
    # results = nr.run(task=ping_task)

    # for host, result in results.items():
    #     print(f"{host}: {result.result}")
    # ping_ip('ya.ru', True)
    print(parse_yaml((get_default_dir()) / "task.yaml.txt", nr))
