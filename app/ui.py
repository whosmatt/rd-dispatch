from monsterui.franken import *
from monsterui.daisy import Alert
from monsterui.franken import P, A

def render_form(error=None):
    form = Form(
        Input(id="url", name="url", placeholder="Enter hoster URL", cls="w-full"),
        Button("Convert", type="submit", cls="mt-2"),
        cls="space-y-2",
        method="post",
        action="/convert"
    )
    content = [H2("Real-Debrid Relay"), form]
    if error:
        content.insert(1, Alert(error, cls="alert-error"))
    return str(Container(*content, cls="max-w-xl mx-auto mt-8"))

def render_result(result):
    filename = result["filename"]
    download_url = result["download_url"]
    link = f"/download?download_url={download_url}&filename={filename}"
    return str(Container(
        H2("Ready to Download"),
        P(f"Filename: {filename}"),
        Button(A("Download", href=link, cls="btn-primary")),
        cls="max-w-xl mx-auto mt-8"
    ))
