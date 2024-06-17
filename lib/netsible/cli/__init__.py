from netsible.cli.main import *
from netsible.cli.config import *
import sys
from importlib.metadata import version
from netsible.modules.cisco import Cisco

if sys.version_info < (3, 10):
    raise SystemExit(
        'ERROR: Netsible requires Python 3.10 or newer on the controller. '
        'Current version: %s' % ''.join(sys.version.splitlines())
    )

jinja2_version = version('jinja2')
if jinja2_version < "3.0.0":
    raise SystemExit(
        'ERROR: Ansible requires Jinja2 3.0 or newer on the controller. '
        'Current version: %s' % jinja2_version
    )

MODULES = {
    'cisco': Cisco,

}