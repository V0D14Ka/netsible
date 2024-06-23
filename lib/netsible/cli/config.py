from netsible.modules.updateint import UpdateInt
from netsible.modules.ospf import Ospf
from netsible.modules.bgp import Bgp

version = "Netsible 0.1 beta"

METHODS = {
    'cisco_ios': {'int': 'sh ip int br',
                  'vlan': 'sh vlan br',
                  'route': 'sh ip route',
                  'lldp': 'sh lldp neighbors',
                  'config': 'sh running-config'
                  },
    'mikrotik_routeros': {'int': '/interface ethernet pr',
                          'ip': '/ip address pr',
                          'vlan': '/interface vlan pr',
                          'route': '/ip route pr',
                          'config': 'export'
                          },
    'linux': {'int': 'ifconfig',
              'uptime': 'uptime',
              },
}

MODULES = {
    'updateint': {"class": UpdateInt,
                  "dict_params": ["interface_name", "description", "ip_address", "subnet_mask", "mtu", "speed",
                                  "duplex",
                                  "bandwidth", "encapsulation", "authentication", "switchport_mode",
                                  "trunk_allowed_vlans",
                                  "shutdown", "write"],
                  "module_templates": ["cisco_ios", "mikrotik_routeros"]
                  },

    'ospf': {"class": Ospf,
             "dict_params": ["process", "networks", "area", "router_id", "auth"],
             "module_templates": ["cisco_ios", "mikrotik_routeros"],
             },

    'bgp': {"class": Bgp,
            "dict_params": ["as", "networks", "neighbors"],
            "module_templates": ["cisco_ios", "mikrotik_routeros"],
            },
}
