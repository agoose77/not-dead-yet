import aiohttp.web
import pathlib
import mimetypes
import aiohttp.web

LISTENER_JS_TEMPLATE = """
<script type="text/javascript">
let ws = new WebSocket(`ws://${{window.location.host}}{path}`);
ws.onopen = (event) => {{
  ws.send(window.location.pathname);
}};
ws.onmessage = (event) => {{
    window.location.reload()
}}
</script>
"""


class InjectedStaticResource(aiohttp.web.StaticResource):
    """Static resource which injects a websocket listener to HTML pages"""

    def __init__(self, ws_path, *args, **kwargs):
        self._payload = LISTENER_JS_TEMPLATE.format(path=ws_path)
        super().__init__(*args, **kwargs)

    async def _handle(self, *args, **kwargs):
        response = await super()._handle(*args, **kwargs)

        if not isinstance(response, aiohttp.web.FileResponse):
            return response

        if mimetypes.guess_type(response._path) != ("text/html", None):
            return response

        content = response._path.read_text()
        result = aiohttp.web.Response(
            text=self._payload + content, content_type="text/html"
        )

        return result
