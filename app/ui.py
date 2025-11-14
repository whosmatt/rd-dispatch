from monsterui.franken import *
from monsterui.daisy import Loading, LoadingT, Toast, ToastVT, ToastHT
from monsterui.franken import P, A, Ul, Li

def render_form(error=None):
    form = Form(
        Input(id="url", name="url", placeholder="Enter URL", cls="w-full"),
        Button(
            Loading(cls=(LoadingT.spinner, LoadingT.lg, "absolute left-4 top-1/2 -translate-y-1/2"), htmx_indicator=True),
            "Convert",
            type="submit",
            cls=(ButtonT.secondary, "w-full", "relative")
        ),
        cls="space-y-2",
        action="/convert",
        hx_post="/convert",
        hx_target="body"
    )
    content = [
        H3(A("rd-dispatch", href="https://github.com/whosmatt/rd-dispatch")),
        DividerSplit(cls="h-3 mb-2"),
        H6("Download any link ", A("supported", href="/hosts", cls=(AT.primary)), " by Real-Debrid (no Torrents ...yet)", cls=(TextPresets.muted_sm, "mb-4")),
        form
    ]
    container = Container(*content, cls="max-w-xl mx-auto mt-8")
    if error:
        toast = Toast(
            error,
            dur=10,
            cls=[ToastVT.bottom, ToastHT.center],
            alert_cls="text-white bg-red-500 border-red-500"
        )
        return container, toast
    return container

def render_result(result):
    filename = result["filename"]
    download_url = result["download_url"]
    link = f"/download?download_url={download_url}&filename={filename}"
    return Container(
        H3("Download Ready"),
        DividerSplit(cls="h-3 mb-2"),
        P(f"{filename}", cls="mb-3"),
        Button("Download", cls=(ButtonT.primary, "w-full"), hx_on_click=f"window.location='{link}'"),
        Button("Go back", cls=(ButtonT.default, "w-full", "mt-2"), hx_on_click="window.location='/'"),
        cls="max-w-xl mx-auto mt-8"
    )

def render_hosts(hosts):
    host_list = Ul(
        *[Li(host) for host in hosts],
        cls=ListT.striped
    )
    return Container(
        H3("Supported Hosts"),
        DividerSplit(cls="h-3 mb-2"),
        Button("Go back", cls=(ButtonT.default, "w-full", "mb-4"), hx_on_click="window.location='/'"),
        H6("The following hosts are currently supported by Real-Debrid:", cls=(TextPresets.muted_sm, "mb-2")),
        host_list,
        cls="max-w-xl mx-auto mt-8"
    )