from fasthtml.common import *
from monsterui.all import *
from starlette.responses import StreamingResponse
from config import get_settings
from rd_client import unrestrict
from relay import stream_file
from ui import render_form, render_result
from auth import require_auth

settings = get_settings()

app, rt = fast_app(hdrs=Theme.blue.headers())

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
    form = await request.form()
    url = form.get("url", "").strip()
    if not url:
        return render_form(error="Please enter a URL.")
    try:
        result = unrestrict(url)
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
        def generate():
            for chunk in stream_file(download_url):
                yield chunk
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            # "Accept-Ranges": "bytes",  # Uncomment for future range support
        }
        return StreamingResponse(generate(), headers=headers, media_type="application/octet-stream")
    except Exception as e:
        return Response(f"Download failed: {e}", status_code=502)

if __name__ == "__main__":
    serve()
