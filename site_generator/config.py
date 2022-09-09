import pathlib
import shutil
from typing import Optional

import pydantic


class SiteGeneratorConfig(pydantic.BaseSettings):
    class Config(pydantic.BaseConfig):
        env_prefix = "SG_"
        orm_mode = True

    templates: pathlib.Path
    pages: pathlib.Path
    output: pathlib.Path
    static: pathlib.Path

    default_template: str = "default.html"

    host: str = "localhost"
    port: str = "8000"

    verbose: bool = False
    force_rebuild: bool = False

    @pydantic.validator("templates", "pages", "static")
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

    @pydantic.validator("output")
    @classmethod
    def ensure_directory_clean(cls, path: Optional[pathlib.Path]):
        """Pydantic validator to ensure the specified path is an empty directory."""
        if path is None:
            return None

        path = path.absolute()

        if path.exists():
            assert path.is_dir(), f"{path} is a file, expected directory"
            shutil.rmtree(path)

        path.mkdir(parents=True)

        return path
