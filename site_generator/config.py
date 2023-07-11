import contextlib
import pathlib
import re

import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


class SiteGeneratorConfig(BaseSettings):
    """General configuration values for `site_generator`, populated from CLI args."""

    model_config = SettingsConfigDict(env_prefix="SG_", from_attributes=True)

    command: str

    base: pathlib.Path
    templates: pathlib.Path
    pages: pathlib.Path
    output: pathlib.Path
    static: pathlib.Path

    default_template: str = "default.html"

    blog_posts_per_page: int = 5

    host: str = "localhost"
    port: str = "8000"

    verbose: bool = False
    dead_links: bool = False
    allowed_links: list[re.Pattern] = pydantic.Field(..., default_factory=list)

    debug_pages: bool = True

    locale: str | None = None
    site_name: str | None = None

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

    def format_relative_path(self, path: pathlib.Path | str) -> str:
        """
        Call `path.relative_to(SiteGeneratorConfig.base)` and return the result.

        If any error occurs while calling `relative_to` the original `path` is returned
        unmodified.
        """
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

        When running in live mode, this assumes `http` and uses both the configured host
        and port values. Otherwise, this assumes `https` and uses only the host value.

        >>> cfg.base_url()
        'https://example.com'
        """
        scheme = "http" if self.command == "live" else "https"
        fqdn = f"{self.host}:{self.port}" if self.command == "live" else self.host
        return f"{scheme}://{fqdn}"
