import dataclasses
import pathlib
from typing import Annotated, Any

import cyclopts
from cyclopts.types import Directory

from weaving import log

app = cyclopts.App(name="weaving")


@app.meta.default
def launcher(
    *tokens: Annotated[str, cyclopts.Parameter(show=False, allow_leading_hyphen=True)],
    verbose: Annotated[
        bool,
        cyclopts.Parameter(
            negative=(), help="Print verbose output details.", group="Commands"
        ),
    ] = False,
) -> Any:
    """Custom launcher for root `weaving` `cyclopts.App`."""
    log.configure(verbose=verbose)
    return app(tokens)


@cyclopts.Parameter(name="*", group="Site config")
@dataclasses.dataclass()
class SiteConfig:
    """Common site config parameters as a group."""

    pages: Directory = pathlib.Path("pages")
    """Source directory for site pages."""

    templates: Directory = pathlib.Path("templates")
    """Source directory for page templates."""

    static: Directory = pathlib.Path("static")
    """Source directory for site static files."""

    root: cyclopts.types.Directory = pathlib.Path()
    """Common root directory for site contents."""

    def __post_init__(self) -> None:
        self.pages = self.pages.resolve()
        self.templates = self.templates.resolve()
        self.static = self.static.resolve()
        self.root = self.root.resolve()
