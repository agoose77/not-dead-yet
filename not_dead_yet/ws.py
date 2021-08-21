import asyncio
import logging

import aiohttp.web

logger = logging.getLogger(__name__)


class WebsocketHandler:
    def __init__(self, notifier):
        self.notifier = notifier

    @staticmethod
    def _get_notifier(ws):
        async def f():
            await ws.send_str("reload!")

        return lambda: asyncio.ensure_future(f())

    async def __call__(self, request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)

        token = None
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == "close":
                    await ws.close()
                else:
                    token = self.notifier.subscribe(self._get_notifier(ws))

            elif msg.type == aiohttp.WSMsgType.ERROR:
                if token is not None:
                    self.notifier.unsubscribe(token)
                logger.error("ws connection closed with exception %s" % ws.exception())
