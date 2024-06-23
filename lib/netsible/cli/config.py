from netsible.modules.updateint import UpdateInt

version = "Netsible 0.1 beta"

methods_cisco_dir = {
    'int': 'sh ip int br',
    'vlan': 'sh vlan br',
    'route': 'sh ip route',
    'lldp': 'sh lldp neighbors',
    'uptime': 'uptime',
    'config': 'sh running-config'
}

methods_linux_dir = {
    'ip': 'ifconfig',
    'uptime': 'uptime',
}

MODULES = {
    'updateint': {"class": UpdateInt,
                  "dict_params": ["interface_name", "description", "ip_address", "subnet_mask", "mtu", "speed",
                                  "duplex",
                                  "bandwidth", "encapsulation", "authentication", "switchport_mode",
                                  "trunk_allowed_vlans",
                                  "shutdown", "write"],
                  "module_template": ["cisco_ios", "mikrotik_routeros"]
                  }
}
