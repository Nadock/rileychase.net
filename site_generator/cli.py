from __future__ import annotations

import argparse
import asyncio
import pathlib
import sys
from typing import TYPE_CHECKING

from site_generator import commands, config, errors, logging

if TYPE_CHECKING:
    from collections.abc import Callable


class SiteGeneratorCLI:
    """Main CLI logic for the site generator."""

    def __init__(self) -> None:
        self.root_parser = argparse.ArgumentParser(
            prog="site_generator", add_help=False
        )

    def _setup_parser(self) -> None:
        self.root_parser.add_argument(
            "--help",
            "-h",
            action="store_true",
            default=False,
            help="Show this message and exit.",
        )
        self.root_parser.add_argument(
            "--templates",
            "-t",
            type=pathlib.Path,
            default="./templates",
            metavar="PATH",
            help="Template files to use when rendering.",
        )
        self.root_parser.add_argument(
            "--pages",
            "-p",
            type=pathlib.Path,
            default="./pages",
            metavar="PATH",
            help="Markdown pages to render into site pages via templates.",
        )
        self.root_parser.add_argument(
            "--static",
            "-s",
            type=pathlib.Path,
            default="./static",
            metavar="PATH",
            help="Static files that are required to fully display the rendered site.",
        )
        self.root_parser.add_argument(
            "--output",
            "-o",
            type=pathlib.Path,
            default="./output",
            metavar="PATH",
            help="Rendered file output location.",
        )
        self.root_parser.add_argument(
            "--verbose",
            "-v",
            default=False,
            action="store_true",
            help="Enable verbose logging output.",
        )
        self.root_parser.add_argument(
            "--site-name",
            type=str,
            default=None,
            metavar="NAME",
            help="The name for this site, used in Open Graph tags.",
        )
        self.root_parser.add_argument(
            "--locale",
            type=str,
            default=None,
            metavar="LOCALE",
            help="The locale of this website, used in Open Graph tags.",
        )

        command_parsers = self.root_parser.add_subparsers(dest="command")

        live_parser = command_parsers.add_parser(
            "live",
            help="Run a live reload server version of the site.",
        )
        live_parser.add_argument(
            "--host",
            type=str,
            default="localhost",
            metavar="HOST",
            help="Hostname to listen at when running in live mode.",
        )
        live_parser.add_argument(
            "--port",
            "-p",
            type=str,
            default="8000",
            metavar="PORT",
            help="Port number to listen on when running in live mode.",
        )
        live_parser.add_argument(
            "--exclude-debug",
            action="store_false",
            dest="debug_pages",
            default=True,
            help="Exclude debug type pages that would normally be included.",
        )

        build_parser = command_parsers.add_parser(
            "build",
            help="Build a fully rendered site and then exit.",
        )
        build_parser.add_argument(
            "--host",
            type=str,
            default="localhost",
            metavar="HOST",
            help="Hostname the site will be hosted under.",
        )
        build_parser.add_argument(
            "--include-debug",
            action="store_true",
            dest="debug_pages",
            default=False,
            help="Include debug type pages that would normally be excluded.",
        )

        validate_parser = command_parsers.add_parser(
            "validate",
            help="Validate source file for semantic errors",
        )
        validate_parser.add_argument(
            "--dead-links",
            default=False,
            action="store_true",
            help="Check a website build for any dead links.",
        )
        validate_parser.add_argument(
            "--allow-link",
            default=[],
            action="append",
            dest="allowed_links",
            type=str,
            help="Regex pattern for a URL that is explicitly allowed.",
        )

    def run(self, argv: list[str]) -> None:
        """Setup and run `site_generator` CLI from args."""
        self._setup_parser()

        args = self.root_parser.parse_args(argv)
        if args.help or not args.command:
            self.root_parser.print_help(sys.stderr)
            return

        args.base = pathlib.Path().resolve()

        cfg = config.SiteGeneratorConfig.model_validate(args)
        logger = logging.configure_logging(cfg)

        for key, value in cfg.dict().items():
            logger.debug(f"config.{key} = {value}")

        cmd = self._get_command(cfg)
        try:
            asyncio.run(cmd())
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            errors.log_error(ex)

    def _get_command(self, cfg: config.SiteGeneratorConfig) -> Callable:
        if cfg.command == "live":
            return commands.live(cfg)
        if cfg.command == "build":
            return commands.build(cfg)
        if cfg.command == "validate":
            return commands.validate(cfg)

        raise ValueError(f"Unknown command name '{cfg.command}'")
