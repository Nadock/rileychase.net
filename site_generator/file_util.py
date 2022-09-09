import pathlib
from typing import Optional

from site_generator import logging

LOGGER = logging.getLogger()


def is_outdated(source: Optional[pathlib.Path], dest: Optional[pathlib.Path]) -> bool:
    """
    Compares two files to see if the `dest` file is older than the `source` file.
    """
    if source is None or not source.exists() or not source.is_file():
        return True
    if dest is None or not dest.exists() or not dest.is_file():
        return True
    return source.stat().st_mtime_ns > dest.stat().st_mtime_ns
