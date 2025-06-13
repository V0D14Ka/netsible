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
 network {{ network.ip }} {{ network.subnet_mask }} area {{ network.area }}
{% endfor %}

{% if auth is defined %}
int {{ auth.int }}
ip ospf authentication-key 0 {{ auth.pass }}
ip ospf authentication
{% endif %}
'''

template_router_os = """
{% if router_id is defined %}
/routing ospf instance
set [ find default=yes ] router-id={{ router_id }}
{% endif %}

/routing ospf network
{% for network in networks %}
add network={{ network.ip }}/{{ network.subnet_mask }} area={{ network.area }}
{% endfor %}

{% if auth is defined %}
/routing ospf interface
add interface={{ auth.int }} network-type=broadcast
set [ find default-name={{ auth.int }} ] authentication=simple authentication-key={{ auth.pass }}
{% endif %}
"""

dict_params = ["process", "zone", "networks", "area", "router_id", "auth"]

module_template = {
    'cisco_ios': template_cisco,
    'mikrotik_routeros': template_router_os
}


class Ospf(BasicModule):

    def run(self, **kwargs):
        super().run(**kwargs)

        if self.client_info['platform'] == 'cisco_ios':
            for network in self.params.get('networks', []):
                try:
                    cidr = int(network['subnet_mask'])
                    subnet_mask = (0xFFFFFFFF >> (32 - cidr)) << (32 - cidr)
                    wildcard_mask = ~subnet_mask & 0xFFFFFFFF
                    wildcard_mask_str = '.'.join([str((wildcard_mask >> (8 * i)) & 0xFF) for i in range(4)[::-1]])

                    network['subnet_mask'] = wildcard_mask_str
                except ValueError:
                    continue

        elif self.client_info['platform'] == 'mikrotik_routeros':
            for network in self.params.get('networks', []):
                try:
                    area = int(network['area'])

                    if area == 0:
                        network['area'] = 'backbone'

                except ValueError:
                    continue

        return self.ssh_connect_and_execute(self.client_info['platform'], self.client_info['hostname'],
                                            self.client_info['username'], self.client_info['password'],
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
            print(commands)
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
