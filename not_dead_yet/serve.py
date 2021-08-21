import asyncio
import logging
import uuid

import aiohttp.web

from .notifier import Notifier
from .watcher import FileWatcher
from .resource import InjectedStaticResource
from .ws import WebsocketHandler

logger = logging.getLogger(__name__)


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


async def run_static_server(
    root_dir,
    host="localhost",
    port=8080,
    dt=1 / 60,
    ignore_patterns=None,
    listener_port=9000,
    watch_files=True,
):
    app = aiohttp.web.Application()

    # Register WS under random UUID
    ws_path = f"/{uuid.uuid4()}/subscribe"

    # Setup notifier for clients
    notifier = Notifier()
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

    # Listen on a port for reloads
    def _accept_connection(reader, writer):
        async def task():
            writer.write("Reloading...".encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            notifier.notify()
        asyncio.ensure_future(task())

    listener = asyncio.start_server(_accept_connection, host=host, port=listener_port)
    coros_or_futures = [
        _run_web_app(app, host=host, port=port),
        listener,
    ]

    # Optionally watch files
    if watch_files:
        # Check files for changes
        watcher = FileWatcher(notifier, root_dir, ignore_patterns=ignore_patterns)
        coros_or_futures.append(watcher.run(dt=dt))

    logger.info(f"Running on http://{host}:{port}/")
    await asyncio.gather(*coros_or_futures)
