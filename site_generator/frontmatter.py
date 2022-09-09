import datetime
import pathlib

import pydantic

from site_generator import config as _config
from site_generator import file_util


class PageFrontmatter(pydantic.BaseModel):

    file: pathlib.Path

    template: str | None = None
    path: str | None = None

    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    date: datetime.date | None = None

    meta: dict | None = None

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

        path = (self.config.output / path).absolute()
        if not path.name.endswith(".html"):
            path = path / "index.html"

        return path

    def is_outdated(self) -> bool:
        return file_util.is_outdated(self.file, self.get_output_path())
