import sys

from site_generator import cli

c = cli.SiteGeneratorCLI()
c.run(sys.argv[1:])
