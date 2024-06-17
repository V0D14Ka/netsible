from netmiko import ConnectHandler


class BasicModule:
    client_info = None
    task_name = None
    module = None
    params = None

    def run(self, **kwargs):
        self.task_name = kwargs['task_name']
        self.client_info = kwargs['client_info']
        self.module = kwargs['module']
        self.params = kwargs['params']

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