from __future__ import annotations

import contextlib
import pathlib
import re  # noqa: TC003

import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


class SiteGeneratorConfig(BaseSettings):
    """General configuration values for `weaving`, populated from CLI args."""

    model_config = SettingsConfigDict(env_prefix="SG_", from_attributes=True)

    command: str
    """The CLI command that was invoked to run the site generator."""
    verbose: bool = False
    """Enable verbose debug logging."""
    debug_pages: bool = True
    """Include `debug` type pages in the generated site output."""

    base: pathlib.Path
    """The base directory the site generator is running from."""
    templates: pathlib.Path
    """The root directory from which to discover Jinja templates."""
    pages: pathlib.Path
    """The root directory from which to discover source markdown pages."""
    static: pathlib.Path
    """The root directory from which to discover static files."""
    output: pathlib.Path
    """The root directory to write out generated site files."""

    default_template: str = "default.html"
    """The default template name, used when a page doesn't specify a template."""

    blog_posts_per_page: int = 5
    """
    The maximum number of blog posts to display per page when generating a `blog_index`
    type page.
    """

    host: str = "localhost"
    """The host to serve the dev site at."""
    port: int = 8080
    """The port to serve the dev site at."""

    dead_links: bool = False
    """Enable dead link detection for the `validation` CLI command."""
    allowed_links: list[re.Pattern] = pydantic.Field(default_factory=list)
    """Patterns for URLs that are allowed without checking in dead link detection."""

    locale: str | None = None
    """The site locale for OpenGraph tags or other purposes."""
    site_name: str | None = None
    """The site name for OpenGraph tags or other purposes."""

    @pydantic.field_validator("templates", "pages", "static", "base", "output")
    @classmethod
    def ensure_directory(cls, path: pathlib.Path | None) -> pathlib.Path | None:
        """Pydantic validator to ensure the specified path is a directory."""
        if path is None:
            return None

        path = path.absolute()

        if not path.exists():
            path.mkdir(parents=True)
        elif not path.is_dir():
            raise ValueError(f"{path} is a file, expected directory")

        return path

    def format_relative_path(self, path: pathlib.Path | str | bytes) -> str:
        """
        Call `path.relative_to(SiteGeneratorConfig.base)` and return the result.

        If any error occurs while calling `relative_to` the original `path` is returned
        unmodified.
        """
        if isinstance(path, bytes):
            path = pathlib.Path(path.decode("utf-8"))

        if isinstance(path, str):
            path = pathlib.Path(path)

        with contextlib.suppress(Exception):
            path = path.relative_to(self.base)

        if path.is_absolute():
            return str(path)
        return f"./{path}"

    def base_url(self) -> str:
        """
        Return the base URL of the site.

        When running in dev mode, this assumes `http` and uses both the configured host
        and port values. Otherwise, this assumes `https` and uses only the host value.

        >>> cfg.base_url()
        'https://example.com'
        """
        scheme = "http" if self.command == "dev" else "https"
        fqdn = f"{self.host}:{self.port}" if self.command == "dev" else self.host
        return f"{scheme}://{fqdn}"
