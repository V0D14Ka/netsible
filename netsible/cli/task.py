import argparse
from pathlib import Path
import sys
import platform
import errno
from netsible.utils.nornir_loader import load_nornir

import yaml
from netsible.cli import BaseCLI
from netsible.cli.config import version as ver
from netsible.cli.config import MODULES

from netsible.utils.utils import init_dir, ping_ip, get_default_dir, Display


def start_task(file_path, nr, debug = False):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            playbook = yaml.safe_load(file)

        Display.debug(f"{file_path} is valid YAML.") if debug else None

        tasks_to_run, hosts, sensitivity = parse_yaml(file_path, nr, debug)
        validate_and_run(tasks_to_run, hosts, sensitivity, debug)

    except yaml.YAMLError as exc:
        Display.error(f"Error in YAML file {file_path}:")
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            Display.error(f"Error position: Line {mark.line + 1}, Column {mark.column + 1}")
        Display.error(exc)

    except ValueError as ve:
        Display.error(f"Validation error: {ve}")

# def parse_yaml(file_path, inv_file):
#     tasks_to_run = []

#     with open(file_path, 'r') as file:
#         playbook_yaml = file.read()
#         playbook = yaml.safe_load(playbook_yaml)
#         # TODO убрать костыли
#         hosts = playbook[0]['hosts']
#         sensitivity = playbook[0]['sensitivity']

#         client_i = None

#         with open(inv_file, 'r') as inv:
#             for line in inv:
#                 client_info = dict(part.split('=') for part in line.strip().split(' '))

#                 if client_info.get('name') == hosts:
#                     client_i = client_info

#         for play in playbook:

#             for task in play['tasks']:
#                 task_name = task['name']
#                 for module, params in task.items():

#                     if module != 'name':
#                         tasks_to_run.append({
#                             'task_name': task_name,
#                             'module': module,
#                             'params': params,
#                             'client_info': client_i,
#                         })

#     return tasks_to_run, hosts, sensitivity

def parse_yaml(file_path, nr, debug):
    tasks_to_run = []

    with open(file_path, 'r') as file:
        playbook = yaml.safe_load(file)
        hosts_name = playbook[0]['hosts']
        sensitivity = playbook[0].get('sensitivity', 'no')

        # Получаем список host объектов, может быть один или несколько
        hosts_list = []

        # 1) Проверка — хост ли это
        if hosts_name in nr.inventory.hosts:
            hosts_list.append(nr.inventory.hosts[hosts_name])
        # 2) Проверка — группа ли это
        elif hosts_name in nr.inventory.groups:
            group_obj = nr.inventory.groups[hosts_name]
            # Получаем хостов, входящих в группу (с учетом наследования)
            for host_name, host_obj in nr.inventory.hosts.items():
                # Проверяем, состоит ли хост в группе
                if hosts_name in host_obj.groups:
                    hosts_list.append(host_obj)
        else:
            raise ValueError(f"Host or group '{hosts_name}' not found in inventory")

        Display.debug(f"List of hosts for tasks: {hosts_list}") if debug else None

        for play in playbook:
            for task in play.get('tasks', []):
                task_name = task['name']
                for module, params in task.items():
                    if module == 'name':
                        continue
                    # Для каждого хоста создаем задачу
                    for host_obj in hosts_list:
                        client_i = {
                            'name': host_obj.name,
                            'hostname': host_obj.hostname,
                            'username': host_obj.username,
                            'password': host_obj.password,
                            'platform': host_obj.platform,
                            'host': host_obj.hostname,
                            # ... другие параметры, если нужны
                        }
                        tasks_to_run.append({
                            'task_name': task_name,
                            'module': module,
                            'params': params,
                            'client_info': client_i,
                        })

    return tasks_to_run, hosts_name, sensitivity

def validate_and_run(tasks_to_run, hosts, sensitivity, debug):
    # Validation part

    Display.debug("Starting validation loop")if debug else None
    for task in tasks_to_run:
        Display.debug("Start task validation") if debug else None
        if task['client_info'] is None:
            Display.error(f"Critical error. Can't get host '{hosts}'.")
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

    # Launch part
    for task in tasks_to_run:
        Display.debug(
            f"Running task '{task['task_name']}' on '{task['client_info']['name']}' using module '{task['module']}' with params {task['params']}") if debug else None

        status_code = (MODULES.get(task['module']).get('class'))().run(task_name=task['task_name'],
                                                                       client_info=task['client_info'],
                                                                       module=task['module'], params=task['params'],
                                                                       sensitivity=sensitivity)
        if status_code == 200:
            continue

        if status_code == 401:
            Display.error(f'Unable to connect - "{task["client_info"]["host"]}", aborting tasks (sensitivity = yes)')
            return

        Display.error(f'Unable to connect - "{task["client_info"]["host"]}", skipping task (sensitivity = no)')


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

            start_task(str(task_file), nr, self.args.debug)
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
