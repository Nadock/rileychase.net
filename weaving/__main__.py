import asyncio
import contextlib
import sys

from weaving import cli

with contextlib.suppress(KeyboardInterrupt):
    sys.exit(asyncio.run(cli.main()))
