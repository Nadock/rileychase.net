import argparse
import asyncio
import pathlib
import sys

from site_generator import commands, config, logging


class SiteGeneratorCLI:
    def __init__(self):
        self.root_parser = argparse.ArgumentParser(
            prog="site_generator", add_help=False
        )

    def _setup_parser(self):
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
            "--force",
            "-f",
            default=False,
            action="store_true",
            help="Force a full rebuild of the site, even if output files are up to date.",
        )

        command_parsers = self.root_parser.add_subparsers(dest="command")

        dev_parser = command_parsers.add_parser(
            "live",
            help="Run a live reload server version of the site.",
        )
        dev_parser.add_argument(
            "--host",
            type=str,
            default="localhost",
            metavar="HOST",
            help="Hostname to listen at when running in live mode.",
        )
        dev_parser.add_argument(
            "--port",
            "-p",
            type=str,
            default="8000",
            metavar="PORT",
            help="Port number to listen on when running in live mode.",
        )

        build_parser = command_parsers.add_parser(
            "build",
            help="Build a fully rendered site and then exit.",
        )

    def run(self, argv: list[str]):
        self._setup_parser()

        args = self.root_parser.parse_args(argv)
        # print(f"{args=}", file=sys.stderr)
        if args.help or not args.command:
            self.root_parser.print_help(sys.stderr)
            return

        cfg = config.SiteGeneratorConfig.from_orm(args)
        logger = logging.configure_logging(cfg)
        logger.debug(f"Staring site_generator with config: {cfg}")

        cmd = self._get_command(args.command, cfg)
        asyncio.run(cmd())

    def _get_command(self, command: str, cfg: config.SiteGeneratorConfig):
        if command == "live":
            return commands.live(cfg)

        if command == "build":
            return commands.build(cfg)

        raise ValueError(f"Unknown command name '{command}'")
