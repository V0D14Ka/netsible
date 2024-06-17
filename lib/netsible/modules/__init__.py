from netmiko import ConnectHandler
from netsible.utils.utils import Display

dict_params = ["int", "cmd"]


class BasicModule:
    client_info = None
    task_name = None
    module = None
    params = None
    dict_params = ["int", "cmd"]

    @staticmethod
    def static_params():
        return dict_params

    def run(self, **kwargs):
        self.task_name = kwargs['task_name']
        self.client_info = kwargs['client_info']
        self.module = kwargs['module']
        self.params = kwargs['params']

        for i in self.params:
            if i not in self.dict_params:
                raise SystemExit(f'ERROR: Incorrect param - "{i}".')

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
