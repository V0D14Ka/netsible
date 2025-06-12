import os
from pathlib import Path

from netsible.utils.utils import Display

MODULE_TEMPLATE = '''from netsible.modules import BasicModule
from jinja2 import Template

template_example = """
! Example configuration for {{ interface_name }}
"""

dict_params = ["interface_name", "description"]

module_template = {{
    "cisco_ios": template_example
}}

class {class_name}(BasicModule):

    def run(self, **kwargs):
        super().run(**kwargs)
        return self.ssh_connect_and_execute(
            self.client_info['platform'],
            self.client_info['hostname'],
            self.client_info['username'],
            self.client_info['password'],
            self.sensitivity
        )

    @staticmethod
    def static_params():
        return dict_params, module_template
'''

def create_module(module_name: str):
    module_dir = Path.home() / ".netsible" / "modules"
    module_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{module_name.lower()}.py"
    filepath = module_dir / filename

    if filepath.exists():
        Display.error(f"Module '{module_name}' already exists in {filepath}")
        return

    class_name = ''.join(word.capitalize() for word in module_name.split('_'))

    with open(filepath, "w") as f:
        f.write(MODULE_TEMPLATE.format(class_name=class_name))

    Display.success(f"Module '{module_name}' created in {filepath}")
