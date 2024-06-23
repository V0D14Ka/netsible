import os

from netmiko import ConnectHandler
from netsible.modules import BasicModule
from jinja2 import Template
from netsible.utils.utils import Display

template_cisco = '''
router ospf {{ process}}
{% if router_id is defined %}
router-id {{ router_id }}
{% endif %}

{% for network in networks %}
 network {{ network.ip }} {{ network.wildcard }} area {{ network.area }}
{% endfor %}

{% if auth is defined %}
int {{ auth.int }}
ip ospf authentication-key 0 {{ auth.pass }}
ip ospf authentication
{% endif %}

'''

dict_params = ["process", "zone", "networks", "area", "router_id", "auth"]

module_template = {
    'cisco_ios': template_cisco,
}


class Ospf(BasicModule):

    def run(self, **kwargs):
        super().run(**kwargs)
        return self.ssh_connect_and_execute(self.client_info['type'], self.client_info['host'],
                                            self.client_info['user'], self.client_info['pass'],
                                            self.sensitivity)

    @staticmethod
    def static_params():
        return dict_params, module_template

    def ssh_connect_and_execute(self, device_type, hostname, user, password, sensitivity, command=None, keyfile=None,
                                port=22):

        try:
            device = {
                'device_type': device_type,
                'host': hostname,
                'port': port,
                'username': user,
                'password': password,
                'secret': 'admin',  # Enable пароль, если он требуется
                'verbose': True,  # включить вывод подробной информации о подключении
            }

            _, mt = self.static_params()
            template = Template(mt.get(device_type))
            output = template.render(self.params)
            commands = [line for line in output.splitlines() if line.strip()]
            print(sensitivity)

            with ConnectHandler(**device) as net_connect:
                net_connect.enable()
                output = net_connect.send_config_set(commands)
                Display.success(f"-------------- Device {device['host']} --------------\n {output}\n -------------- "
                                f"END --------------")

            return 200

        except Exception as e:
            if self.sensitivity == "yes":
                return 401

            return 402
