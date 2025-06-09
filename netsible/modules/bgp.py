import os

from netmiko import ConnectHandler
from netsible.modules import BasicModule
from jinja2 import Template
from netsible.utils.utils import Display

dict_params = ["as", "networks", "neighbors"]

template_cisco = '''
router bgp {{ as }}

{% for network in networks %}
 network {{ network.ip }} mask {{ network.subnet_mask }}
{% endfor %}

{% for neighbor in neighbors %}
 neighbor {{ neighbor.ip }} remote-as {{ neighbor.as }}
 
 {% if next_hop_self is defined %}
    neighbor {{ neighbor.ip }} name {{ neighbor.name }}
 {% endif %}
 
 {% if next_hop_self is defined %}
    neighbor {{ neighbor.ip }} next_hop_self
 {% endif %}
 
 {% if route_reflector is defined %}
    neighbor {{ neighbor.ip }} route_reflector-client
 {% endif %}
 
{% endfor %}

do write
'''

template_router_os = """

/routing bgp
instance set 0 as={{ as }}

{% for network in networks %}
network add network={{ network.ip }}/{{ network.subnet_mask }}
{% endfor %}

{% for neighbor in neighbors %}
peer add name={{ neighbor.name }} remote-address={{ neighbor.ip }} remote-as={{ neighbor.ip }}
{% endfor %}
"""

module_template = {
    'cisco_ios': template_cisco,
    'mikrotik_routeros': template_router_os
}


class Bgp(BasicModule):

    def run(self, **kwargs):
        super().run(**kwargs)

        if self.client_info['type'] == 'cisco_ios':
            for network in self.params.get('networks', []):
                try:
                    cidr = int(network['subnet_mask'])
                    subnet_mask = (0xFFFFFFFF >> (32 - cidr)) << (32 - cidr)
                    subnet_mask_str = '.'.join([str((subnet_mask >> (8 * i)) & 0xFF) for i in range(4)[::-1]])

                    network['subnet_mask'] = subnet_mask_str
                except ValueError:
                    pass

        print(self.params)
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

            # raise e
