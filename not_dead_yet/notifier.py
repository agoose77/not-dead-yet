import asyncio
import logging
import os
import time

logger = logging.getLogger(__name__)


def scandir_walk(path):
    for entry in os.scandir(path):
        if entry.is_dir():
            yield from scandir_walk(entry.path)
        else:
            yield entry


def _most_recent_mtime(directory):
    last_mtime = 0
    for p in scandir_walk(directory):
        mtime = p.stat().st_mtime
        if mtime > last_mtime:
            last_mtime = mtime
    return last_mtime


class FileNotifier:
    class _Token:
        def __init__(self, notifier):
            self._notifier = notifier

    def __init__(self, directory):
        self._directory = directory
        self._notifiers = set()

    def subscribe(self, notifier):
        self._notifiers.add(notifier)
        return self._Token(notifier)

    def unsubscribe(self, token):
        self._notifiers.remove(token._item)

    def notify(self):
        for f in self._notifiers:
            try:
                f()
            except Exception:
                logger.exception("Failed to invoke notifier")
        self._notifiers.clear()

    async def run(self, dt=1 / 60):
        last_notified_mtime = time.time()

        while True:
            await asyncio.sleep(dt)

            # Determine when most recent file change occurred
            last_changed_mtime = await asyncio.get_running_loop().run_in_executor(
                None, _most_recent_mtime, self._directory
            )

            if last_changed_mtime > last_notified_mtime:
                self.notify()

            # Update notifications
            last_notified_mtime = last_changed_mtime
