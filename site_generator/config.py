import pathlib
import shutil
from typing import Optional

import pydantic


class SiteGeneratorConfig(pydantic.BaseSettings):
    class Config(pydantic.BaseConfig):
        env_prefix = "SG_"
        orm_mode = True

    base: pathlib.Path
    templates: pathlib.Path
    pages: pathlib.Path
    output: pathlib.Path
    static: pathlib.Path

    default_template: str = "default.html"

    host: str = "localhost"
    port: str = "8000"

    verbose: bool = False

    @pydantic.validator("templates", "pages", "static", "base", "output")
    @classmethod
    def ensure_directory(cls, path: Optional[pathlib.Path]):
        """Pydantic validator to ensure the specified path is a directory."""
        if path is None:
            return None

        path = path.absolute()

        if path.exists():
            assert path.is_dir(), f"{path} is a file, expected directory"
        else:
            path.mkdir(parents=True)

        return path

    def format_relative_path(self, path: pathlib.Path | str) -> str:
        """
        Call `path.relative_to(SiteGeneratorConfig.base)` and return the result.

        If any error occurs while calling `relative_to` the original `path` is returned
        unmodified.
        """
        if isinstance(path, str):
            path = pathlib.Path(path)

        try:
            path = path.relative_to(self.base)
        except Exception:
            pass

        if path.is_absolute():
            return str(path)
        return f"./{path}"
