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

    @staticmethod
    def static_params():
        return dict_params, module_template

    def prepare(self):
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

        return super().prepare()

