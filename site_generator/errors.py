from site_generator import logging

LOGGER = logging.getLogger()


class SiteGeneratorError(Exception):
    pass


class PipelineError(SiteGeneratorError):
    pass


def log_error(ex: Exception):
    if isinstance(ex, SiteGeneratorError):
        LOGGER.error(ex)
        LOGGER.debug(ex, exc_info=True)
        return

    LOGGER.error(ex, exc_info=True)
    raise ex
