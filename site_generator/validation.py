from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING
from urllib import parse

import aiofile
import aiostream
import bs4
import httpx

from site_generator import config, errors, markdown

if TYPE_CHECKING:
    import pathlib
    from collections.abc import AsyncGenerator


class Validator:
    """Site validation logic."""

    def __init__(self, cfg: config.SiteGeneratorConfig) -> None:
        self.cfg = cfg
        self._lock = asyncio.Lock()
        self._link_cache: dict[str, httpx.Response] = {}
        self._client = httpx.AsyncClient(
            http2=True, timeout=10.0, follow_redirects=True, max_redirects=10
        )

    async def validate(self) -> AsyncGenerator[errors.ValidationError, None]:
        """
        Run all of the configured site validators, yielding validation errors as they
        are discovered.
        """
        streams = [self.validate_markdown()]
        if self.cfg.dead_links:
            streams.append(self.validate_dead_links())

        async with aiostream.stream.merge(*streams).stream() as stream:
            async for error in stream:
                yield error

    async def validate_markdown(self) -> AsyncGenerator[errors.ValidationError, None]:
        """
        Validate markdown sources, yielding validation errors as they are discovered.
        """
        async for page in markdown.find_markdown(self.cfg.pages):
            content, fm = await markdown.load_markdown(self.cfg, page)

            if not content and fm.get_meta().get("validation", {}).get("content", True):
                yield errors.ValidationError(file=page, error="content: page is empty")

            for error in fm.validate_frontmatter():
                yield errors.ValidationError(file=page, error=f"frontmatter: {error}")

    async def validate_dead_links(self) -> AsyncGenerator[errors.ValidationError, None]:
        """
        Validate output HTML for dead links, yielding validation errors as they are
        discovered.
        """
        if not self.cfg.output.is_dir():
            raise errors.SiteGeneratorError(
                "Site must be built before it can be validated for dead links."
            )

        # Reset valid links cache
        async with self._lock:
            self._link_cache = {}

        # Discover all *.html files
        streams = []
        for path in self.cfg.output.glob("**/*.html"):
            streams.append(self._validate_dead_links(path))

        # Yield all errors as they are found
        async with aiostream.stream.merge(*streams).stream() as stream:
            async for error in stream:
                yield error

    async def _validate_dead_links(
        self, path: pathlib.Path
    ) -> AsyncGenerator[errors.ValidationError, None]:
        # Load and parse the HTML, then find all the `<a>` tags
        async with aiofile.async_open(path, encoding="utf-8") as file:
            content = await file.read()
        soup = bs4.BeautifulSoup(content, features="html.parser")
        anchors: bs4.ResultSet[bs4.Tag] = soup.find_all("a", recursive=True)

        coros = []
        for tag in anchors:
            link = tag.attrs.get("href")

            # If there is no link or the link is explicitly allowed, skip it
            if not link or any(p.match(link) for p in self.cfg.allowed_links):
                continue

            if parse.urlparse(link).hostname:
                coros.append(
                    self._validate_web_link(path, link, tag.sourceline, tag.sourcepos)
                )
            else:
                coros.append(
                    self._validate_site_link(path, link, tag.sourceline, tag.sourcepos)
                )

        # Yield results as they become available
        for coro in asyncio.as_completed(coros):
            error = await coro
            if error is not None:
                yield error

    async def _read_html_output(self) -> AsyncGenerator[tuple[pathlib.Path, str], None]:
        async def _read_file(p: pathlib.Path) -> tuple[pathlib.Path, str]:
            async with aiofile.async_open(p, encoding="utf-8") as file:
                return (p, await file.read())

        coros = []
        for path in self.cfg.output.glob("**/*.html"):
            coros.append(_read_file(path))

        for coro in asyncio.as_completed(coros):
            yield await coro

    async def _validate_web_link(
        self, path: pathlib.Path, link: str, line: int | None, pos: int | None
    ) -> errors.ValidationError | None:
        """
        Validate a link to an external site by performing a `HTTP HEAD` operation and
        checking the response code.
        """
        async with self._lock:
            if link not in self._link_cache:
                with contextlib.suppress(Exception):
                    self._link_cache[link] = await self._client.head(link)

        resp = self._link_cache.get(link)
        if resp and 200 <= resp.status_code < 300:  # noqa: PLR2004
            return None

        return errors.ValidationError(
            file=path,
            error=(
                f"dead link: {link}: "
                + (f"HTTP {resp.status_code}" if resp else "no response")
            ),
            line=line,
            char=pos,
        )

    async def _validate_site_link(
        self, path: pathlib.Path, link: str, line: int | None, pos: int | None
    ) -> errors.ValidationError | None:
        """
        Validate a link to another page on this site by determining it's destination and
        ensuring there is a page generated for it.
        """
        if link.startswith("mailto:"):
            if len(link.split("mailto:")[-1].split("@")) == 2:  # noqa: PLR2004
                return None
            return errors.ValidationError(
                file=path, error=f"invalid email: {link}", line=line, char=pos
            )

        link = link.removeprefix("/").removesuffix("/")
        if "." not in link.split("/")[-1]:
            link = "/".join([*link.split("/"), "index.html"]).removeprefix("/")

        link_p = path.parent / link if link.startswith(".") else self.cfg.output / link

        if link_p.is_file():
            return None

        return errors.ValidationError(
            file=path,
            error=f"dead link: {link}: expected to find {link_p}",
            line=line,
            char=pos,
        )
