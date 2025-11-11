import os
from flask import Flask, request, Response, redirect, url_for, render_template_string, abort
from config import get_settings
from rd_client import unrestrict
from relay import stream_file
from ui import render_form, render_result

app = Flask(__name__)
settings = get_settings()

@app.route("/", methods=["GET"])
def index():
    return render_form()

@app.route("/convert", methods=["POST"])
def convert():
    url = request.form.get("url", "").strip()
    if not url:
        return render_form(error="Please enter a URL.")
    try:
        result = unrestrict(url)
    except ValueError as e:
        return render_form(error=str(e))
    except Exception as e:
        return render_form(error="Error contacting Real-Debrid.")
    return render_result(result)

@app.route("/download")
def download():
    download_url = request.args.get("download_url")
    filename = request.args.get("filename", "file")
    if not download_url:
        abort(400, "Missing download URL.")
    try:
        def generate():
            for chunk in stream_file(download_url):
                yield chunk
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/octet-stream",
            # "Accept-Ranges": "bytes",  # Uncomment for future range support
        }
        return Response(generate(), headers=headers)
    except Exception as e:
        abort(502, f"Download failed: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
