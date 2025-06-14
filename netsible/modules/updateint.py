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
{% endif %}

{% if description is not defined and ip_address is not defined and mtu is not defined and speed is not defined and duplex is not defined and bandwidth is not defined and encapsulation is not defined and authentication is not defined and switchport_mode is not defined and shutdown is not defined %}
 no shutdown
{% endif %}'''

template_router_os = '''
/interface ethernet
{% if mtu is defined %}
 set [ find default-name={{ interface_name }} ] mtu={{ mtu }}
{% endif %}

{% if description is defined %}
 set [ find default-name={{ interface_name }} ] comment="{{ description }}"
{% endif %}

{% if speed is defined %}
 {% if auto-negotiation == no %}
 set [ find default-name={{ interface_name }} ] auto-negotiation=no speed={{ speed }}
 {% elif auto-negotiation == yes%}
 set [ find default-name={{ interface_name }} ] auto-negotiation=yes advertise={{ speed }}
 {% else %}
 ; You must provide auto-negotiation param to change speed
 {% endif %}
{% endif %}

{% if duplex is defined %}
 {% if duplex == 'full' %}
 set [ find default-name={{ interface_name }} ] full-duplex=yes
 {% elif duplex == 'auto' %}
 set [ find default-name={{ interface_name }} ] full-duplex=no
 {% endif %}
{% endif %}

{% if shutdown %}
 set [ find default-name={{ interface_name }} ] disabled=yes
{% else %}
 set [ find default-name={{ interface_name }} ] disabled=no
{% endif %}

{% if ip_address is defined and subnet_mask is defined %}
 /ip address add address={{ ip_address }}/{{ subnet_mask }} interface={{ interface_name }}
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

'''

dict_params = ["interface_name", "description", "ip_address", "subnet_mask", "mtu", "speed", "duplex",
               "bandwidth", "encapsulation", "authentication", "switchport_mode", "trunk_allowed_vlans",
               "shutdown", "write"]

module_template = {
    'cisco_ios': template_cisco,
    'mikrotik_routeros': template_router_os
}


class UpdateInt(BasicModule):

    @staticmethod
    def static_params():
        return dict_params, module_template

    def prepare(self):
        if self.client_info['platform'] == 'cisco_ios':
            try:
                cidr = int(self.params['subnet_mask'])
                subnet_mask = (0xFFFFFFFF >> (32 - cidr)) << (32 - cidr)
                subnet_mask_str = '.'.join([str((subnet_mask >> (8 * i)) & 0xFF) for i in range(4)[::-1]])

                self.params['subnet_mask'] = subnet_mask_str
            except ValueError:
                pass
        
        return super().prepare()
