import logging


_factory = logging.getLogRecordFactory()


def _record_factory(*args, **kwargs):
    record = _factory(*args, **kwargs)
    record.relative_seconds = record.relativeCreated / 1000
    return record


logging.basicConfig(format="[{levelname}] {relative_seconds:.3f}s {message}", style="{")
logging.getLogger().setLevel(logging.DEBUG)
logging.setLogRecordFactory(_record_factory)
