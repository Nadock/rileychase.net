import asyncio
import pathlib
import queue
from typing import Literal, Union

from site_generator import config, markdown, static

_ptype = Union[Literal["static"], Literal["markdown"]]


class PipelineManager:
    def __init__(self, _config: config.SiteGeneratorConfig) -> None:
        self._queues: dict[_ptype, queue.Queue] = {
            "static": queue.Queue(),
            "markdown": queue.Queue(),
        }
        self._coroutines: dict[_ptype, asyncio.Task] = {}
        self._watchers: list[asyncio.Task] = []
        self.config = _config
        self.running = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    def start(self):
        """
        Start the `PipelineManager`.

        Once the `PipelineManager` is started, any pipeline requests that are, or have
        been, `enqueue`d will run. The manager ensure that for each source file only
        one instance of it's corresponding pipeline is running at any one time.

        Any subsequent requests to run the same pipeline for the same path while a
        previous pipeline execution is still running will be queued until the first
        execution finishes.

        The manager must be stopped safely via the `stop` method, the manager acts as
        a context manager to make this easy.
        """
        if self.running:
            raise ValueError(f"{self.__class__.__name__} is already running")
        self.running = True
        for pipeline in self._queues:
            self._watchers.append(asyncio.create_task(self._watch(pipeline)))

    def stop(self):
        """
        Stop the `Pipeline` manager by first stopping any new pipelines being queued
        and then cancelling any in-progress pipelines.
        """
        for task in self._watchers:
            task.cancel()
        for task in self._coroutines.values():
            task.cancel()

    def enqueue(self, path: pathlib.Path, pipeline: _ptype):
        """
        Enqueue a `path` to be run through the relevant `pipeline`.

        The valid options for the `pipeline` name are `"static"`, and `"markdown"`.

        The enqueued execution of the pipeline will not occur immediately, instead it
        is scheduled and will run when the queue is next checked and no other pipeline
        of the same type for the path is currently running.

        Enqueued pipeline executions will not start running until `start` has been called.
        """
        self._queues[pipeline].put(path)

    async def _watch(self, pipeline: _ptype):
        """
        Watch the specified `pipeline` queue and start pipeline executions as needed.
        """
        while True:
            path = self._queues[pipeline].get()
            prev_coro = self._coroutines.get(path)

            if not prev_coro or prev_coro.done():
                # If we're not currently processing this path, then start a task to
                # process it again now.
                self._coroutines[path] = asyncio.create_task(
                    self._pipeline(pipeline, path)
                )
            else:
                # Otherwise, put it back in the queue until the previous task is
                # complete.
                self._queues[pipeline].put(path)

    async def _pipeline(self, pipeline: _ptype, path: pathlib.Path):
        """Run an execution of the specified `pipeline` and `path`."""
        if pipeline == "static":
            await static.static_pipeline(self.config, path)
        elif pipeline == "markdown":
            await markdown.markdown_pipeline(self.config, path)
        else:
            raise ValueError(f"{pipeline} is not the name of a known pipeline")
