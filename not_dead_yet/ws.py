import asyncio
import logging

import aiohttp.web

logger = logging.getLogger(__name_)


class WebsocketHandler:
    def __init__(self, resource, notifier):
        self.resource = resource
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
                    path = self.resource.resolve_path(msg.data)
                    token = self.notifier.subscribe(path, self._get_notifier(ws))

            elif msg.type == aiohttp.WSMsgType.ERROR:
                if token is not None:
                    self.notifier.unsubscribe(token)
                logger.error("ws connection closed with exception %s" % ws.exception())
