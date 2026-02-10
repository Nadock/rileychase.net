import argparse
import pathlib
import sys
from typing import Protocol, override

import anyio

from weaving import config, dev, errors, logging, pipeline, validation

LOGGER = logging.getLogger()


class Command(Protocol):
    """CLI command protocol type."""

    @classmethod
    def setup(cls, parser: argparse.ArgumentParser) -> None:
        """Setup and command specific CLI flags & args."""

    @classmethod
    async def run(cls, cfg: config.SiteGeneratorConfig) -> None:
        """Run the command."""


class Build(Command):
    """Build a fully rendered site and then exit."""

    @override
    @classmethod
    def setup(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--host",
            type=str,
            default="localhost",
            metavar="HOST",
            help="Hostname the site will be hosted under.",
        )

    @override
    @classmethod
    async def run(cls, cfg: config.SiteGeneratorConfig) -> None:
        await pipeline.pipeline(cfg)


class Validate(Command):
    """Validate source file for semantic errors."""

    @override
    @classmethod
    def setup(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--dead-links",
            default=False,
            action="store_true",
            help="Check a website build for any dead links.",
        )
        parser.add_argument(
            "--allow-link",
            default=[],
            action="append",
            dest="allowed_links",
            type=str,
            help="Regex pattern for a URL that is explicitly allowed.",
        )

    @override
    @classmethod
    async def run(cls, cfg: config.SiteGeneratorConfig) -> None:
        LOGGER.info("Starting site validation")

        count = 0
        async for error in validation.Validator(cfg).validate():
            error_msg = f"[{error.file.relative_to(cfg.base)}] {error.error}"
            if error.line and error.char:
                error_msg += f" on line {error.line}, column {error.char}"
            LOGGER.error(error_msg)
            count += 1

        if count > 0:
            LOGGER.error(f"{count} validation error{'s' if count > 1 else ''} found")
            sys.exit(count)

        LOGGER.info("No validation errors found")


class Dev(Command):
    """Run a dev server version of the site."""

    @override
    @classmethod
    def setup(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--host",
            type=str,
            default="localhost",
            metavar="HOST",
            help="Hostname to listen at when running in dev mode.",
        )
        parser.add_argument(
            "--port",
            "-p",
            type=int,
            default=8080,
            metavar="PORT",
            help="Port number to listen on when running in dev mode.",
        )

    @override
    @classmethod
    async def run(cls, cfg: config.SiteGeneratorConfig) -> None:
        await dev.watch_and_serve(cfg)


_COMMANDS: dict[str, type[Command]] = {
    "build": Build,
    "dev": Dev,
    "validate": Validate,
}


def setup_argparse() -> argparse.ArgumentParser:
    """Setup an `argparse.ArgumentParser` for the `weaving` CLI."""
    parser = argparse.ArgumentParser(prog="weaving", add_help=False)
    parser.add_argument(
        "--help",
        "-h",
        action="store_true",
        default=False,
        help="Show this message and exit.",
    )
    parser.add_argument(
        "--templates",
        "-t",
        type=pathlib.Path,
        default="./templates",
        metavar="PATH",
        help="Template files to use when rendering.",
    )
    parser.add_argument(
        "--pages",
        "-p",
        type=pathlib.Path,
        default="./pages",
        metavar="PATH",
        help="Markdown pages to render into site pages via templates.",
    )
    parser.add_argument(
        "--static",
        "-s",
        type=pathlib.Path,
        default="./static",
        metavar="PATH",
        help="Static files that are required to fully display the rendered site.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=pathlib.Path,
        default="./output",
        metavar="PATH",
        help="Rendered file output location.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        default=False,
        action="store_true",
        help="Enable verbose logging output.",
    )
    parser.add_argument(
        "--site-name",
        type=str,
        default=None,
        metavar="NAME",
        help="The name for this site, used in Open Graph tags.",
    )
    parser.add_argument(
        "--locale",
        type=str,
        default=None,
        metavar="LOCALE",
        help="The locale of this website, used in Open Graph tags.",
    )
    parser.add_argument(
        "--exclude-debug",
        action="store_false",
        dest="debug_pages",
        default=False,
        help="Exclude debug type pages that would normally be included.",
    )
    parser.add_argument(
        "--include-debug",
        action="store_true",
        dest="debug_pages",
        default=False,
        help="Include debug type pages that would normally be excluded.",
    )

    command_parsers = parser.add_subparsers(
        title="commands", dest="command", metavar="COMMAND"
    )
    for name, cmd in _COMMANDS.items():
        cmd.setup(command_parsers.add_parser(name=name, help=cmd.__doc__))

    return parser


async def main() -> None:
    """Run the `weaving` CLI."""
    parser = setup_argparse()

    args = parser.parse_args()
    if args.help or not args.command:
        parser.print_help(sys.stderr)
        return

    args.base = pathlib.Path(await anyio.Path.cwd())

    cfg = config.SiteGeneratorConfig.model_validate(args)
    logger = logging.configure_logging(cfg)

    for key, value in cfg.model_dump().items():
        logger.debug(f"config.{key} = {value}")

    try:
        cmd = _COMMANDS[cfg.command]
    except KeyError:
        raise ValueError(f"Unknown command name '{cfg.command}'") from None

    try:
        await cmd.run(cfg)
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        errors.log_error(ex)
