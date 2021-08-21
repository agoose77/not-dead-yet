import asyncio
import logging
import uuid

import aiohttp.web

from .notifier import FileNotifier
from .resource import InjectedStaticResource
from .ws import WebsocketHandler

logger = logging.getLogger((__name__))


async def _run_web_app(app, host="localhost", port=8080, event=None):
    if event is None:
        event = asyncio.Event()

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host, port)
    await site.start()

    try:
        await event.wait()
    except asyncio.CancelledError:
        raise
    finally:
        await runner.cleanup()


async def run_app(root_dir, host="localhost", port=8080, dt=1 / 60):
    app = aiohttp.web.Application()

    # Register WS under random UUID
    ws_path = f"/{uuid.uuid4()}/subscribe"

    # Setup notifier for clients
    notifier = FileNotifier(root_dir)
    handler = WebsocketHandler(notifier)
    app.router.add_routes([aiohttp.web.get(ws_path, handler)])

    # Create static resource
    resource = InjectedStaticResource(
        ws_path=ws_path,
        prefix="",
        directory=root_dir,
        show_index=True,
        append_version=True,
    )
    app.router.register_resource(resource)

    # Run notifier
    watcher = asyncio.create_task(notifier.run())

    logger.info(f"Running on http://{host}:{port}/")

    await asyncio.gather(watcher, _run_web_app(app))
