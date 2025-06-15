from netsible.core.module_loader import load_custom_modules
from netsible.modules.updateint import UpdateInt
from netsible.modules.ospf import Ospf
from netsible.modules.bgp import Bgp
from netsible.modules.mnapalm import NapalmGetFacts

version = "Netsible 0.1 beta"

METHODS = {
    'cisco_ios': {'int': 'sh ip int br',
                  'int-detail': 'sh int',
                  'ip': 'sh ip int br',
                  'vlan': 'sh vlan br',
                  'route': 'sh ip route',
                  'lldp': 'sh lldp neighbors',
                  'config': 'sh running-config',
                  'system': 'sh version',
                  'ospf-neighbor': 'sh ip ospf neighbor'
                  },
    'mikrotik_routeros': {'int': '/interface ethernet pr',
                          'int-detail': '/interface ethernet pr detail',
                          'ip': '/ip address pr',
                          'vlan': '/interface vlan pr',
                          'route': '/ip route pr',
                          'config': 'export',
                          'system': '/system resource print',
                          'ospf-neighbor': '/routing ospf neighbor pr'
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

    # "napalm_get_facts": {
    #     "class": NapalmGetFacts,
    #     "dict_params": ["test"],  # если не требуется никаких параметров
    #     "module_templates": ["mikrotik_routeros", "junos", "eos", "nxos"],  # дополни при необходимости
    # },
}

MODULES.update(load_custom_modules())