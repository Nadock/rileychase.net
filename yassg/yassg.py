import asyncio
import logging
import pathlib
import time
import functools
from http import server
from typing import AsyncIterable, Dict, Optional

import jinja2
import markdown
from watchdog import events, observers

LOGGER = logging.getLogger(__name__)


class SourceFile:
    def __init__(
        self,
        *,
        file: pathlib.Path,
        source: pathlib.Path,
        dest: pathlib.Path,
        indexify: bool = False,
    ):
        """
        `file` must be the full path to the original source file
        `dest` must be the path to the source directory for unproceessed Markdown
        `dest` must be the path to the destination directory for generated HTML
        """
        # The location of the source directory
        self.source = source
        # The location of the dest directory
        self.dest = dest

        # The location of this file
        self.source_path = file
        # The relative location within the source directory of this file
        self.relative_path = file.relative_to(source)
        # The eventual output location for this file
        if not indexify or file.name == "index.md":
            self.dest_path = (
                dest / self.relative_path.parent / file.name.replace(".md", ".html")
            )
        else:
            self.dest_path = (
                dest
                / self.relative_path.parent
                / file.name.replace(".md", "")
                / "index.html"
            )
        LOGGER.debug(f"{indexify=} -> {self.dest_path=}")

        # The raw contents of this file
        self.content = ""
        # The generated HTML for this file
        self.content_html = ""
        # The generated HTML merged with the relavent template for this file
        self.templated_html = ""
        # The metadata from Markdown frontmatter
        self.meta: Dict[str, str] = {}

    async def read_contents(self, reload: bool = False):
        if not self.content or reload:
            self.content = self.source_path.read_text()

    async def generate_html(self, reload: bool = False):
        await self.read_contents(reload=reload)
        if not self.content_html or reload:
            from pymdownx import emoji

            md = markdown.Markdown(
                extensions=[
                    "markdown.extensions.tables",
                    "markdown.extensions.fenced_code",
                    "markdown.extensions.codehilite",
                    "pymdownx.betterem",
                    "pymdownx.emoji",
                    "pymdownx.highlight",
                    "pymdownx.magiclink",
                    "pymdownx.saneheaders",
                    # "pymdownx.superfences",
                    "pymdownx.tasklist",
                    "pymdownx.tilde",
                    "full_yaml_metadata",
                    "nl2br",
                ],
                output_format="html",
                extension_configs={
                    "pymdownx.emoji": {
                        "emoji_index": emoji.gemoji,
                        "emoji_generator": emoji.to_svg,
                    },
                    "pymdownx.tasklist": {
                        "custom_checkbox": True,
                    },
                },
            )

            self.content_html = md.convert(self.content)
            self.meta = getattr(md, "Meta", dict())

    async def is_valid(self):
        if not self.source_path.exists():
            LOGGER.debug(f"Ignoring file {self.relative_path} that doesn't exist")
            return False
        if not self.source_path.name.endswith(".md"):
            LOGGER.debug(f"Ignoring non-markdown file {self.relative_path}")
            return False
        return True


class RegenerateWatcher(events.FileSystemEventHandler):
    def __init__(
        self,
        *,
        source: pathlib.Path,
        dest: pathlib.Path,
        static: pathlib.Path,
        templates: pathlib.Path,
        indexify: bool = False,
    ):
        super().__init__()
        self.source = source
        self.dest = dest
        self.static = static
        self.templates = templates
        self.indexify = indexify

    def on_any_event(self, event: events.FileSystemEvent):
        LOGGER.info(f"{event.src_path} {event.event_type}, regenerating site")
        asyncio.run(
            generate(
                source=self.source,
                dest=self.dest,
                static=self.static,
                templates=self.templates,
                indexify=self.indexify,
            )
        )


async def generate(
    *,
    source: pathlib.Path,
    dest: pathlib.Path,
    static: pathlib.Path,
    templates: pathlib.Path,
    indexify: bool = False,
):
    time_0 = time.time_ns()

    # Start a source file pipeline for each source file we can find
    coros = []
    async for file in find_files(source):
        coros.append(
            source_file_pipeline(
                file=file,
                source=source,
                dest=dest,
                templates=templates,
                indexify=indexify,
            )
        )

    # Start a static file pipeline for each static file we can find
    async for file in find_files(static):
        coros.append(static_file_pipeline(file=file, static=static, dest=dest))

    time_1 = time.time_ns()
    LOGGER.info(
        f"Started pipeline for {len(coros)} file{'s' if len(coros) != 1 else ''} in "
        f"{_format_runtime(time_0, time_1)}"
    )

    generated_files = [f for f in await asyncio.gather(*coros) if f]
    time_2 = time.time_ns()
    LOGGER.info(
        f"Pipeline completed for {len(generated_files)} file"
        f"{'s' if len(generated_files) != 1 else ''} in {_format_runtime(time_1, time_2)}"
    )


async def watch_and_rebuild(
    *,
    source: pathlib.Path,
    dest: pathlib.Path,
    static: pathlib.Path,
    templates: pathlib.Path,
    indexify: bool = False,
    host: str = "localhost",
    port: int = 8000,
):
    await generate(
        source=source, dest=dest, static=static, templates=templates, indexify=indexify
    )

    observer = observers.Observer()
    event_handler = RegenerateWatcher(
        source=source, dest=dest, static=static, templates=templates, indexify=indexify
    )

    LOGGER.info(f"Adding recursive watcher for {source}")
    observer.schedule(event_handler, source, recursive=True)
    LOGGER.info(f"Adding recursive watcher for {static}")
    observer.schedule(event_handler, static, recursive=True)
    LOGGER.info(f"Adding recursive watcher for {templates}")
    observer.schedule(event_handler, templates, recursive=True)
    observer.start()

    LOGGER.info(f"Starting webserver on {host}:{port}, press Ctrl-C to exit")
    web_handler = functools.partial(
        server.SimpleHTTPRequestHandler, directory=str(dest)
    )
    with server.ThreadingHTTPServer((host, port), web_handler) as web_server:
        try:
            web_server.serve_forever()
        except KeyboardInterrupt as ex:
            LOGGER.debug("Webserver stopped")
            observer.stop()
            observer.join()
            LOGGER.debug("File watchers stopped")
            raise ex


async def find_files(source: pathlib.Path) -> AsyncIterable[pathlib.Path]:
    if not source.exists():
        return

    iters = []
    for path in source.iterdir():
        if path.is_file():
            yield path
        if path.is_dir():
            iters.append(find_files(path))

    for iter in iters:
        async for file in iter:
            yield file


async def source_file_pipeline(
    *,
    file: pathlib.Path,
    source: pathlib.Path,
    dest: pathlib.Path,
    templates: pathlib.Path,
    indexify: bool,
) -> Optional[pathlib.Path]:
    source_file = SourceFile(file=file, source=source, dest=dest, indexify=indexify)
    # Validity check
    if not await source_file.is_valid():
        LOGGER.info(f"Skipping invalid source file {source_file.relative_path}")
        return None

    # Read contents
    await source_file.read_contents()

    # Get template for current file
    j_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))
    template_name = source_file.meta.get("template", "template.html")
    try:
        template = j_env.get_template(template_name)
    except jinja2.TemplateNotFound as ex:
        LOGGER.debug(
            f"Cannot find template with {template_name=} in {templates=}: {ex}",
            exc_info=True,
        )
        LOGGER.error(f"Cannot find template '{template_name}' in '{str(templates)}'")
        raise ex

    # Outdated check
    not_outdated = False
    LOGGER.debug(f"{template.filename=}")
    if not is_outdated(source_file.source_path, source_file.dest_path):
        if template.filename:
            if not is_outdated(pathlib.Path(template.filename), source_file.dest_path):
                not_outdated = True
        else:
            not_outdated = True

    if not_outdated:
        LOGGER.debug(f"Skipping unchanged source file {source_file.relative_path}")
        return None

    # Generate contents HTML
    await source_file.generate_html()

    # Merge with template
    source_file.templated_html = template.render(
        content=source_file.content_html, meta=source_file.meta
    )

    # Write to dest
    source_file.dest_path.parent.mkdir(parents=True, exist_ok=True)
    source_file.dest_path.write_text(source_file.templated_html)

    # DONE
    LOGGER.debug(f"Finished source file pipeline for {source_file.relative_path}")
    return source_file.dest_path


async def static_file_pipeline(
    *, file: pathlib.Path, static: pathlib.Path, dest: pathlib.Path
) -> Optional[pathlib.Path]:
    dest_path = dest / file.relative_to(static)
    if not is_outdated(file, dest_path):
        LOGGER.debug(f"Skipping unchanged static file {file.relative_to(static)}")
        return None

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(file.read_bytes())
    LOGGER.debug(f"Finished static file pipeline for {file.relative_to(static)}")
    return dest_path


def is_outdated(source: Optional[pathlib.Path], dest: Optional[pathlib.Path]) -> bool:
    """
    Compares two files to see if the `dest` file needs to be regenerated from the
    `source` file.
    """
    if source is None or not source.exists() or not source.is_file():
        return False
    # source is a file that exists
    if dest is None or not dest.exists() or not dest.is_file():
        return True
    # dest is a file that exists
    # Return true if source is newer than dest
    return source.stat().st_mtime_ns > dest.stat().st_mtime_ns


def _format_runtime(t_0: int, t_1: int) -> str:
    """
    Format the elapsed time between two nanosecond time readings from `time.time_ns`.
    """
    t_detla = abs(t_0 - t_1) / (10 ** 9)
    if t_detla < 0.001:
        return "under 1ms"

    return f"{t_detla:.3f}s"
