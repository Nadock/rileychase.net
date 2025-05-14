import asyncio
import contextlib

from weaving import cli

with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(cli.main())
