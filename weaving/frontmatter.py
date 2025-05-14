import datetime
import logging
import pathlib
import re
from typing import Literal
from urllib import parse

import pydantic

from weaving import config as _config

_WHITESPACE_RE = re.compile(r"\s+")

PageType = Literal["default", "blog", "blog_index"]

LOGGER = logging.getLogger(__name__)


class OpenGraphFrontmatter(pydantic.BaseModel):
    """Page Open Graph details extracted from markdown frontmatter content."""

    title: str | None = None
    """The og:title for this page, defaults to the page title if not set."""

    image: str | None = None
    """The og:image for this page."""

    description: str | None = None
    """The og:description for this page, defaults to the page subtitle if not set."""

    url: str | None = None
    """The og:url for this page, defaults to the computed page URL if not set."""

    type: str = "website"
    """The og:type for this page, defaults to `"website"` if not set."""

    locale: str | None = None
    """The og:locale for this page, defaults to the locale in config if not set.."""

    site_name: str | None = None
    """
    The og:site_name for this page, defaults to the site name in config if not set.
    """


class PageFrontmatter(pydantic.BaseModel):
    """Page details extracted from markdown frontmatter content."""

    template: str | None = None
    """
    The name of the template to use when rendering this file.

    The template to render this page will be chosen from the following ordered options:
    1. The `template` frontmatter property.
    2. A template name from the page type — `"{type}.html"`.
    3. The configured default template name — `"default.html"` unless set otherwise.
    """

    title: str | None = None
    """The title for this page."""

    subtitle: str | None = None
    """The subtitle for this page."""

    tags: list[str] = pydantic.Field(default_factory=list)
    """Classification tags for this page's content."""

    date: datetime.date | None = None
    """The original publication date for this page."""

    og: OpenGraphFrontmatter | None = None
    """
    Open Graph details. Some values are auto populated from `title`, `subtitle`, `date`,
    and other sources.
    """

    meta: dict | None = None
    """
    Arbitrary values that can be set on a per-page basis with no further validation or
    prescribed semantic meaning. It depends on the template how these values are used.
    """

    type: PageType = "default"
    """
    `type` is a special keyword that enable bespoke page handling. You normally do not
    need to specify this value, the default has no special meaning. However, you can
    set the page `type` to one of the following values to enable specific
    functionality.

    - `default` is the default value and has no special meaning.
    - `blog` indicates the page is a blog post and should be collated with the nearest
      `blog_index` parent page.
    - `blog_index` marks this page as the root page for a blog. When being processed,
       this file will use the `blog_index` pipeline instead of the default `markdown`
       pipeline. The file must be named `index.md`.
    """

    debug: bool = False
    """Mark this page for local preview only, not included in the regular build."""

    # The following fields are populated automatically, don't need to be in the
    # template frontmatter, and aren't included in template rendering.
    file: pathlib.Path
    config: _config.SiteGeneratorConfig | None = None

    def get_output_path(self) -> pathlib.Path:
        """Determine the output path to write rendered page content into."""
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        path = self.file.parent.relative_to(self.config.pages)
        if self.file.name != "index.md":
            path /= self.file.name.removesuffix(".md")
        path /= "index.html"

        # Replace whitespace with underscores for nice URLs
        path = pathlib.Path(*[_WHITESPACE_RE.sub("_", part) for part in path.parts])

        return (self.config.output / path).resolve()

    def get_page_path(self) -> str:
        """Get the site relative URL path for this page."""
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        return "/" + str(
            self.get_output_path().relative_to(self.config.output)
        ).removesuffix("index.html").removesuffix("/")

    def get_page_url(self) -> str:
        """Get the fully qualified URL for this page."""
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        return parse.urljoin(self.config.base_url(), self.get_page_path())

    def get_open_graph(self) -> OpenGraphFrontmatter:
        """
        Returns the Open Graph frontmatter for this page with default values applied.

        The values actually provided via frontmatter from the source file remain
        unmodified in `self.og`.
        """
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        og = self.og or OpenGraphFrontmatter()

        # Make OG image URL fully qualified if it isn't already
        if og.image and not parse.urlparse(og.image).hostname:
            image = og.image if og.image.startswith("/") else "/" + og.image
            og.image = self.config.base_url() + "/" + image

        # Set default values for OG properties
        og.title = og.title or self.title
        og.description = og.description or self.subtitle
        og.url = og.url or self.get_page_url()
        og.locale = og.locale or self.config.locale
        og.site_name = og.site_name or self.config.site_name

        return og

    def validate_frontmatter(self) -> list[str]:
        """
        Analyse the configured frontmatter values for sematic correctness.

        The validation is above and beyond the Pydantic validation, and is aimed at
        determining if a page's frontmatter is likely to cause build issues.
        """
        errors = []
        validation = self.meta.get("validation", {}) if self.meta else {}

        if not self.title and validation.get("title", True):
            errors.append("no title set")

        if not self.subtitle and validation.get("subtitle", True):
            errors.append("no subtitle set")

        if self.type == "blog_index" and self.file.name != "index.md":
            errors.append("type set to 'blog_index' but file not named `index.md`")

        return errors
