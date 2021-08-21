import asyncio
import logging
import os
import time
import fnmatch

logger = logging.getLogger(__name__)


def scandir_walk(path):
    for entry in os.scandir(path):
        if entry.is_dir():
            yield from scandir_walk(entry.path)
        else:
            yield entry


def _most_recent_mtime(directory, ignore_patterns):
    last_mtime = 0
    for p in scandir_walk(directory):
        # Ignore particular names
        if any(fnmatch.fnmatch(p.name, x) for x in ignore_patterns):
            continue

        mtime = p.stat().st_mtime
        if mtime > last_mtime:
            last_mtime = mtime
    return last_mtime


class FileWatcher:
    def __init__(self, notifier, directory, ignore_patterns=None):
        self._directory = directory
        self._notifier = notifier
        self._ignore_patterns = ignore_patterns or []

    async def run(self, dt=1 / 60):
        last_notified_mtime = time.time()

        while True:
            await asyncio.sleep(dt)

            # Determine when most recent file change occurred
            last_changed_mtime = await asyncio.get_running_loop().run_in_executor(
                None, _most_recent_mtime, self._directory, self._ignore_patterns
            )

            if last_changed_mtime > last_notified_mtime:
                self._notifier.notify()

            # Update notifications
            last_notified_mtime = last_changed_mtime
