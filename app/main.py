from fasthtml.common import *
from monsterui.all import *
from starlette.responses import StreamingResponse
import httpx
import asyncio
from rd_client import RDClient
from relay import stream_file
from ui import render_form, render_result, render_hosts, render_torrent
from auth import require_auth

hdrs = Theme.green.headers() + [
    Style("body { font-family: monospace !important; }")
]
app, rt = fast_app(hdrs=hdrs, title="rd-dispatch")

# RD client instance
rd = RDClient()

@rt
def index(request):
    auth_resp = require_auth(request)
    if auth_resp:
        return auth_resp
    return render_form()

@rt
async def convert(request):
    auth_resp = require_auth(request)
    if auth_resp:
        return auth_resp
    query = request.query_params
    url = query.get("url", "").strip()
    if not url:
        return render_form(error="Please enter a URL.")
    try:
        if url.startswith("magnet:"):
            result = await asyncio.to_thread(rd.add_torrent, url)
            return render_torrent(result)
        result = await asyncio.to_thread(rd.unrestrict, url)
    except ValueError as e:
        return render_form(error=str(e))
    except Exception as e:
        return render_form(error="Error contacting Real-Debrid.")
    return render_result(result)

@rt
def download(request):
    auth_resp = require_auth(request)
    if auth_resp:
        return auth_resp
    query = request.query_params
    download_url = query.get("download_url")
    filename = query.get("filename", "file")
    if not download_url:
        return Response("Missing download URL.", status=400)
    try:
        head_resp = httpx.head(download_url, timeout=10)
        head_resp.raise_for_status()
        file_size = head_resp.headers.get("Content-Length")
        def generate():
            for chunk in stream_file(download_url):
                yield chunk
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        if file_size:
            headers["Content-Length"] = file_size
        return StreamingResponse(generate(), headers=headers, media_type="application/octet-stream")
    except Exception as e:
        return Response(f"Download failed: {e}", status_code=502)

@rt
def hosts(request):
    auth_resp = require_auth(request)
    if auth_resp:
        return auth_resp
    return render_hosts(rd.supported_hosts())

@rt
async def select_files(request):
    auth_resp = require_auth(request)
    if auth_resp:
        return auth_resp
    form = await request.form()
    torrent_id = form.get("torrent_id")
    files = form.getlist("files") if hasattr(form, 'getlist') else []
    try:
        result = await asyncio.to_thread(rd.select_files, torrent_id, files or [])
    except ValueError as e:
        return render_form(error=str(e))
    except Exception:
        return render_form(error="Error contacting Real-Debrid.")
    return render_torrent(result)

serve()
