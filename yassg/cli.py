import asyncio
import logging
import pathlib
import shutil
import sys

import click

from . import yassg

LOGGER = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option(
    "--source",
    type=click.Path(dir_okay=True, readable=True, resolve_path=True),
    default="content",
    metavar="PATH",
    help="The source location for the Markdown files used to genrated the site.",
)
@click.option(
    "--dest",
    type=click.Path(dir_okay=True, writable=True, resolve_path=True),
    default="public",
    metavar="PATH",
    help="The output location for the genrated site.",
)
@click.option(
    "--static",
    type=click.Path(dir_okay=True, readable=True, resolve_path=True),
    default="static",
    metavar="PATH",
    help="The location of static files to include in the genrated site.",
)
@click.option(
    "--templates",
    type=click.Path(dir_okay=True, readable=True, resolve_path=True),
    default="templates",
    metavar="PATH",
    help="The location of template files to use in the genrated site.",
)
@click.option(
    "--clean",
    is_flag=True,
    help="Clear the dest directory and regenerate the whole site.",
)
@click.option(
    "--indexify",
    is_flag=True,
    help="Convert content paths from /name.md to /name/index.html",
)
def cli(
    ctx: click.Context,
    source: str,
    dest: str,
    static: str,
    templates: str,
    clean: bool,
    indexify: bool,
):
    if clean:
        shutil.rmtree(dest, ignore_errors=True)

    ctx.ensure_object(dict)
    ctx.obj["source"] = source
    ctx.obj["dest"] = dest
    ctx.obj["static"] = static
    ctx.obj["templates"] = templates
    ctx.obj["indexify"] = indexify


@click.command()
@click.pass_context
def generate(ctx):
    try:
        asyncio.run(
            yassg.generate(
                source=pathlib.Path(ctx.obj["source"]),
                dest=pathlib.Path(ctx.obj["dest"]),
                static=pathlib.Path(ctx.obj["static"]),
                templates=pathlib.Path(ctx.obj["templates"]),
                indexify=ctx.obj["indexify"],
            )
        )
    except Exception as ex:
        LOGGER.debug(f"Generate command failed with error: {ex}")
        sys.exit(1)


cli.add_command(generate)


@click.command()
@click.pass_context
@click.option(
    "--host",
    type=str,
    default="localhost",
    metavar="HOST",
    help="The hostname to run the webserver under.",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    metavar="PORT",
    help="The port number to run the webserver under.",
)
def dev(ctx, host: str, port: int):
    try:
        asyncio.run(
            yassg.watch_and_rebuild(
                source=pathlib.Path(ctx.obj["source"]),
                dest=pathlib.Path(ctx.obj["dest"]),
                static=pathlib.Path(ctx.obj["static"]),
                templates=pathlib.Path(ctx.obj["templates"]),
                indexify=ctx.obj["indexify"],
                host=host,
                port=port,
            )
        )
    except Exception as ex:
        LOGGER.debug(f"Generate command failed with error: {ex}")
        sys.exit(1)


cli.add_command(dev)
