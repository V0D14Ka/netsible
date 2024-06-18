import os

from netmiko import ConnectHandler
from netsible.modules import BasicModule
from jinja2 import Template
from netsible.utils.utils import Display

template_cisco = '''
interface {{ interface_name }}
{% if description is defined %}
 description {{ description }}
{% endif %}

{% if ip_address is defined and subnet_mask is defined %}
 ip address {{ ip_address }} {{ subnet_mask }}
{% endif %}

{% if secondary_ip_addresses is defined %}
{% for ip in secondary_ip_addresses %}
 ip address {{ ip.address }} {{ ip.subnet }} secondary
{% endfor %}
{% endif %}

{% if mtu is defined %}
 mtu {{ mtu }}
{% endif %}

{% if speed is defined %}
 speed {{ speed }}
{% endif %}

{% if duplex is defined %}
 duplex {{ duplex }}
{% endif %}

{% if bandwidth is defined %}
 bandwidth {{ bandwidth }}
{% endif %}

{% if encapsulation is defined %}
 encapsulation {{ encapsulation }}
{% endif %}

{% if authentication is defined %}
 authentication {{ authentication }}
{% endif %}

{% if switchport_mode is defined %}
 switchport mode {{ switchport_mode }}
{% if switchport_mode == 'access' and access_vlan is defined %}
 switchport access vlan {{ access_vlan }}
{% endif %}
{% if switchport_mode == 'trunk' and trunk_allowed_vlans is defined %}
 switchport trunk allowed vlan {{ trunk_allowed_vlans }}
{% endif %}
{% if switchport_mode == 'trunk' and native_vlan is defined %}
 switchport trunk native vlan {{ native_vlan }}
{% endif %}
{% endif %}

{% if shutdown %}
 shutdown
{% else %}
 no shutdown
{% endif %}

{% if write %}
 do write
{% else %}

{% if description is not defined and ip_address is not defined and mtu is not defined and speed is not defined and duplex is not defined and bandwidth is not defined and encapsulation is not defined and authentication is not defined and switchport_mode is not defined and shutdown is not defined %}
 no shutdown
{% endif %}'''

template_router_os = '''
/interface {{ interface_name }}
{% if description is defined %}
 description="{{ description }}"
{% endif %}

{% if ip_address is defined and subnet_mask is defined %}
 ip address={{ ip_address }}/{{ subnet_mask }}
{% endif %}

{% if secondary_ip_addresses is defined %}
{% for ip in secondary_ip_addresses %}
 ip address={{ ip.address }}/{{ ip.subnet }} add
{% endfor %}
{% endif %}

{% if mtu is defined %}
 mtu={{ mtu }}
{% endif %}

{% if speed is defined %}
 speed={{ speed }}
{% endif %}

{% if duplex is defined %}
 duplex={{ duplex }}
{% endif %}

{% if bandwidth is defined %}
 tx-rate={{ bandwidth }}
{% endif %}

{% if encapsulation is defined %}
 ; Encapsulation is not directly configurable on MikroTik
{% endif %}

{% if authentication is defined %}
 ; Authentication settings (like MD5) may vary, configure as needed
{% endif %}

{% if switchport_mode is defined %}
 /interface ethernet switch port
 {% if switchport_mode == 'access' and access_vlan is defined %}
 set {{ interface_name }} vlan-mode=secure vlan-header=add \
    default-vlan-id={{ access_vlan }}
 {% endif %}
 {% if switchport_mode == 'trunk' and trunk_allowed_vlans is defined %}
 set {{ interface_name }} vlan-mode=secure vlan-header=add \
    allowed-vlan={{ trunk_allowed_vlans }}
 {% endif %}
 {% if switchport_mode == 'trunk' and native_vlan is defined %}
 set {{ interface_name }} vlan-mode=secure vlan-header=add \
    native-vlan-id={{ native_vlan }}
 {% endif %}
{% endif %}

{% if shutdown %}
 disabled=yes
{% else %}
 disabled=no
{% endif %}

{% if write %}
 /export
{% else %}
{% if description is not defined and ip_address is not defined and mtu is not defined and speed is not defined and duplex is not defined and bandwidth is not defined and encapsulation is not defined and authentication is not defined and switchport_mode is not defined and shutdown is not defined %}
 enabled=yes
{% endif %}
{% endif %}
'''

module_template = {
    'cisco': template_cisco,
    'routeros': template_router_os
}


class UpdateInt(BasicModule):

    def run(self, **kwargs):
        super().run(**kwargs)
        self.ssh_connect_and_execute(self.client_info['type'], self.client_info['host'],
                                     self.client_info['user'], self.client_info['pass'])

    @staticmethod
    def static_params():
        dict_params = ["interface_name", "description", "ip_address", "subnet_mask", "mtu", "speed", "duplex",
                       "bandwidth", "encapsulation", "authentication", "switchport_mode", "trunk_allowed_vlans",
                       "shutdown"]
        return dict_params

    def print_cfg(self):
        template = Template(template_cisco)
        output = template.render(self.params)
        commands = [line for line in output.splitlines() if line.strip()]
        print(commands)

    def ssh_connect_and_execute(self, device_type, hostname, user, password, command=None, keyfile=None, port=22):

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

            template = Template(module_template.get(self.module))
            output = template.render(self.params)
            commands = [line for line in output.splitlines() if line.strip()]

            with ConnectHandler(**device) as net_connect:
                net_connect.enable()
                output = net_connect.send_config_set(commands)
                Display.success(f"-------------- Device {device['host']} --------------\n {output}\n -------------- "
                                f"END --------------")

        except Exception as e:
            raise e
