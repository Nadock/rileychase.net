from site_generator import logging

LOGGER = logging.getLogger()


class SiteGeneratorError(Exception):
    """Base exception class for any `site_generator` errors."""


class PipelineError(SiteGeneratorError):
    """Pipeline failure for a specific source file."""


def log_error(ex: Exception) -> None:
    """Log an exception according to what kind of exception it is."""
    if isinstance(ex, SiteGeneratorError):
        LOGGER.error(ex)
        LOGGER.debug(ex, exc_info=True)
        return

    LOGGER.error(ex, exc_info=True)
    raise ex
