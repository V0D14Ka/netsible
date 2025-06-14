import os
from pathlib import Path

from netsible.utils.utils import Display

MODULE_TEMPLATE = '''from netsible.modules import BasicModule
from jinja2 import Template

dict_params = ["example_param"]

template_example = """
! Example configuration for {{{{ example_param }}}}
"""

module_template = {{
	"example_os": template_example
}}

class {class_name}(BasicModule):

    @staticmethod
    def static_params():
        return dict_params, module_template

    def prepare(self):
    
        # Your code here
    
        return super().prepare()

'''


def create_module(module_name: str, template: bool = False):
    module_dir = Path.home() / ".netsible" / "modules"
    module_dir.mkdir(parents=True, exist_ok=True)

    template_dir = Path.home() / ".netsible" / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{module_name.lower()}.py"
    filepath = module_dir / filename

    if filepath.exists():
        Display.error(f"Module '{module_name}' already exists in {filepath}")
        return

    class_name = ''.join(word.capitalize() for word in module_name.split('_'))

    with open(filepath, "w") as f:
        f.write(MODULE_TEMPLATE.format(class_name=class_name))

    Display.success(f"Module '{module_name}' created in {filepath}")

    if template:
        template_filepath = template_dir / filename

        if filepath.exists():
            Display.error(f"Template '{module_name}' already exists in {template_filepath}")
            return

        template_filepath.touch()

        Display.success(f"Template '{module_name}' created in {filepath}")
