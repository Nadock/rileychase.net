import asyncio
import contextlib

from site_generator import cli

with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(cli.main())
