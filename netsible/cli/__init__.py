# from netsible.cli.main import *
# from netsible.cli.config import *
import sys
from importlib.metadata import version

from netsible.utils.utils import Display, init_dir

if sys.version_info < (3, 10):
    raise SystemExit(
        'ERROR: Netsible requires Python 3.10 or newer on the controller. '
        'Current version: %s' % ''.join(sys.version.splitlines())
    )

jinja2_version = version('jinja2')
if jinja2_version < "3.0.0":
    raise SystemExit(
        'ERROR: Netsible requires Jinja2 3.0 or newer on the controller. '
        'Current version: %s' % jinja2_version
    )

class BaseCLI:
    @classmethod
    def cli_start(cls, args=None):
        try:
            init_dir()
            try:
                if args is None:
                    args = sys.argv
                    # TODO validation
            except UnicodeError:
                Display.error('Command line args are not in utf-8, unable to continue.  '
                              'Netsible currently only understands utf-8')
            else:
                cli = cls(args)
                cli.run()

        except KeyboardInterrupt:
            Display.error("User interrupted execution")

        # sys.exit(exit_code)