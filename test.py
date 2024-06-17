import yaml

# Пример плейбука в виде строки
playbook_yaml = '''
---
- name: 'Execute a script on all web server nodes'
  hosts: web_nodes
  tasks:
    - name: "Cisco test task"
      cisco:
        path: "/etc/resolv.conf"
        line: "nameserver 10.1.250.10"
'''

# Загружаем YAML-данные с помощью safe_load
playbook = yaml.safe_load(playbook_yaml)


# Имитация выполнения задач (упрощённый пример)
def execute_playbook(playbook):
    for play in playbook:
        print(f"Executing play: {play['name']}")
        for task in play['tasks']:
            task_name = task['name']
            for module, params in task.items():
                if module != 'name':
                    print(f"Running task '{task_name}' using module '{module}' with params {params}")
                    # Здесь будет вызов соответствующего модуля Ansible
                    # В реальном сценарии Ansible выполнит соответствующий модуль
                    # Например, для модуля 'lineinfile' будет вызвано что-то вроде:
                    # ansible.modules.lineinfile.run(params)

# Выполнение плейбука
# execute_playbook(playbook)
print(playbook[0]['hosts'])