import logging
import sys

from site_generator import config


def configure_logging(cfg: config.SiteGeneratorConfig) -> logging.Logger:
    """Setup root `logging.Logger` objects to print to stderr nicely."""
    root = logging.getLogger()

    app = root.getChild("site_generator")
    app.propagate = False

    root.setLevel(logging.ERROR)
    if cfg.verbose:
        app.setLevel(logging.DEBUG)
    else:
        app.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    handler.formatter = formatter

    app.addHandler(handler)
    root.addHandler(handler)

    return app


def getLogger(name: str | None = None) -> logging.Logger:  # noqa: N802
    """Alias function for `logging.getLogger` that ensures we use the app logger."""
    name = f"site_generator.{name}" if name else "site_generator"
    return logging.getLogger(name)
