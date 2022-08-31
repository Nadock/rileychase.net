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
    output: Optional[pathlib.Path]

    host: Optional[str]
    port: Optional[str]

    @pydantic.validator("templates", "pages")
    def ensure_directory(cls, path: Optional[pathlib.Path]):
        if path is None:
            return None

        path = path.absolute()

        if path.exists():
            assert path.is_dir(), f"{path} is a file, expected directory"
        else:
            path.mkdir(parents=True)

        return path

    @pydantic.validator("output")
    def ensure_directory_clean(cls, path: Optional[pathlib.Path]):
        if path is None:
            return None

        path = path.absolute()

        if path.exists():
            assert path.is_dir(), f"{path} is a file, expected directory"
            shutil.rmtree(path)

        path.mkdir(parents=True)

        return path
