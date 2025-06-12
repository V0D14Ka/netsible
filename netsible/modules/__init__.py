from netmiko import ConnectHandler
from netsible.utils.utils import Display


class BasicModule:
    client_info = None
    task_name = None
    module = None
    params = None
    sensitivity = None

    @staticmethod
    def static_params():
        dict_params = ["int", "cmd"]
        return dict_params

    def print_cfg(self):
        return

    def run(self, **kwargs):
        self.task_name = kwargs['task_name']
        self.client_info = kwargs['client_info']
        self.module = kwargs['module']
        self.params = kwargs['params']
        self.sensitivity = kwargs['sensitivity']

    def ssh_connect_and_execute(self, device_type, hostname, user, password, command, keyfile=None, port=22):

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
        except:
            pass
