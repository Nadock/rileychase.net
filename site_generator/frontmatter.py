import datetime
import pathlib

import pydantic

from site_generator import config as _config


class PageFrontmatter(pydantic.BaseModel):

    # The following fields can be set via the template's frontmatter

    ## The name of the template to use when rendering this file
    template: str | None = None

    ## The path under which the page should be located, if different from the relative
    ## structure of the pages directory.
    ## If this path does not end in `.html` it will have `index.html` appended so the
    ## path works as expected in browsers.
    path: str | None = None

    ## `title`, `subtitle`, `description`, and `tags` can each be used to describe the
    ## page and it's content. It depends on the template how these are used, for
    ## example you can use the `title` to set the `.head.title` DOM field's text.
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    tags: list[str] = pydantic.Field(default_factory=list)
    date: datetime.date | None = None

    meta: dict | None = None

    # The following fields are populated automatically and don't need to be in the
    # template frontmatter
    file: pathlib.Path
    config: _config.SiteGeneratorConfig | None = None

    def get_template_name(self) -> str:
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        if self.template:
            return self.template
        if self.config.default_template:
            return self.config.default_template
        return "default.html"

    def get_output_path(self) -> pathlib.Path:
        if not self.config:
            raise ValueError(f"{self.__class__.__name__}.config must be set")

        if not self.path:
            base = self.file.parent.relative_to(self.config.pages)
            name = self.file.name.replace(".md", ".html")
            path = base / name
        else:
            path = pathlib.Path(self.path)

        path = (self.config.output / path).resolve()
        if not path.name.endswith(".html"):
            path = path / "index.html"

        return path
