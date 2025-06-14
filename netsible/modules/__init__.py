from jinja2 import Template
from netmiko import ConnectHandler
from netsible.utils.utils import Display

dict_params = []
module_template = {}

class BasicModule:
    name = None
    client_info = None
    task_name = None
    module = None
    params = None
    sensitivity = None
    path_to_conf = None

    def __init__(self, **kwargs):
        self.client_info = kwargs['client_info']
        self.name = self.client_info['name']
        self.task_name = kwargs['task_name']
        self.module = kwargs['module']
        self.params = kwargs['params']
        self.sensitivity = kwargs['sensitivity']
        # self.path_to_conf = kwargs['path_to_conf'].get(self.name, None)

        self.device = {
                'device_type': self.client_info['platform'],
                'host': self.client_info['hostname'],
                'port': self.client_info['port'],
                'username': self.client_info['username'],
                'password': self.client_info['password'],
                'secret': 'admin',  # Enable пароль, если он требуется
                'verbose': True,  # включить вывод подробной информации о подключении
            }

    @staticmethod
    def static_params():
        return dict_params, module_template
    
    def prepare(self, **kwargs):
        return self.generate_cfg()

    def generate_cfg(self):
        _, mt = self.static_params()
        template = Template(mt.get(self.client_info['platform']))
        self.output = template.render(self.params)
        self.commands = [line for line in self.output.splitlines() if line.strip()]
        return self.output, self.commands
    

    def run(self):

        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                output = net_connect.send_config_set(self.commands)

            return 200, output

        except Exception as e:
            if self.sensitivity == "yes":
                return 401, None

            return 402, None
