import importlib.util
import os
import sys
from pathlib import Path

def load_custom_modules(custom_dir="~/.netsible/modules"):
    modules = {}
    custom_path = Path(os.path.expanduser(custom_dir))

    if not custom_path.exists():
        return modules

    sys.path.append(str(custom_path))

    for py_file in custom_path.glob("*.py"):
        module_name = py_file.stem

        spec = importlib.util.spec_from_file_location(module_name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type):  # Класс
                # Регистрируем только если это подкласс BasicModule
                from netsible.modules import BasicModule
                if issubclass(obj, BasicModule) and obj is not BasicModule:
                    modules[module_name] = {
                        "class": obj,
                        "dict_params": obj.static_params()[0],
                        "module_templates": list(obj.static_params()[1].keys())
                    }
    return modules