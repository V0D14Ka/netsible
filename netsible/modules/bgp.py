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

    @staticmethod
    def static_params():
        return dict_params, module_template

    def prepare(self):
        if self.client_info['platform'] == 'cisco_ios':
            for network in self.params.get('networks', []):
                try:
                    cidr = int(network['subnet_mask'])
                    subnet_mask = (0xFFFFFFFF >> (32 - cidr)) << (32 - cidr)
                    subnet_mask_str = '.'.join([str((subnet_mask >> (8 * i)) & 0xFF) for i in range(4)[::-1]])

                    network['subnet_mask'] = subnet_mask_str
                except ValueError:
                    pass

        return super().prepare()
