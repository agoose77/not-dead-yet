import asyncio
import logging

logger = logging.getLogger(__name__)


class FileNotifier:
    class _Token:
        def __init__(self, item):
            self._item = item

    def __init__(self):
        self._notifiers = set()

    def subscribe(self, path, notify):
        item = (path, notify)
        self._notifiers.add(item)
        return self._Token(item)

    def unsubscribe(self, token):
        self._notifiers.remove(token._item)

    async def run(self, dt=1 / 60):
        modified_times = {}
        while True:
            await asyncio.sleep(dt)

            notified = []

            for item in self._notifiers:
                path, notify = item

                new_time = path.stat().st_mtime
                last_time = modified_times.get(path, new_time)
                modified_times[path] = new_time

                if new_time == last_time:
                    continue

                try:
                    notify()
                except Exception:
                    logger.exception("Failed to notify listener")
                finally:
                    notified.append(item)

            # Remove notified listeners
            for item in notified:
                self._notifiers.remove(item)
