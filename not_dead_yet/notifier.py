import logging

logger = logging.getLogger(__name__)


class Notifier:
    class _Token:
        def __init__(self, notifier):
            self._notifier = notifier

    def __init__(self):
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
