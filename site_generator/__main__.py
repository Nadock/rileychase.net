import sys

from . import cli

c = cli.SiteGeneratorCLI()
c.run(sys.argv[1:])
