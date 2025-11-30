from monsterui.franken import *
from monsterui.daisy import Loading, LoadingT, Toast, ToastVT, ToastHT
from monsterui.franken import P, A, Ul, Li, Img, Div, Span

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
    # hosts is a list of dicts: {domain, name, image, status}
    items = []
    for h in hosts:
        domain = h.get("domain")
        name = h.get("name")
        img = h.get("image")
        status = h.get("status")
        badge_cls = "bg-green-100 text-green-800" if status == "up" else "bg-red-100 text-red-800"
        host_item = DivLAligned(
            Img(src=img, cls=("w-4 h-4 rounded mr-3 object-cover") if img else ("w-4 h-4 rounded mr-3 bg-gray-200")),
            Div(
                H6(name),
                P(domain, cls=(TextPresets.muted_sm, "text-xs"))
            ),
            Span(status.capitalize() if status else "Unknown", cls=("px-2 py-1 rounded-full text-sm ml-auto", badge_cls)),
            cls=("items-center flex w-full")
        )
        items.append(Li(host_item))

    host_list = Ul(*items, cls=ListT.striped)

    return Container(
        H3("Supported Hosts"),
        DividerSplit(cls="h-3 mb-2"),
        Button("Go back", cls=(ButtonT.default, "w-full", "mb-4"), hx_on_click="window.location='/'"),
        H6("The following hosts are currently supported by Real-Debrid:", cls=(TextPresets.muted_sm, "mb-2")),
        host_list,
        cls="max-w-xl mx-auto mt-8"
    )


def render_torrent(info):
    # normalize list -> dict
    if isinstance(info, list) and info:
        info = info[0]

    title = info.get("original_filename") or info.get("filename") or info.get("id")
    status = info.get("status")
    progress = info.get("progress")
    files = info.get("files") or []

    items = []
    for f in files:
        fid = f.get("id")
        path = f.get("path")
        size = f.get("bytes")
        selected = f.get("selected")
        checkbox = LabelCheckboxX(path, id=f"file_{fid}", name="files", value=str(fid), checked=bool(selected))
        items.append(Li(checkbox))

    file_list = Ul(*items, cls=ListT.striped) if items else P("No files yet")

    select_form = Form(
        Input(type="hidden", name="torrent_id", value=info.get("id")),
        file_list,
        Div(
            Button("Select All", type="button", cls=(ButtonT.secondary, "mr-2"), hx_on_click="document.querySelectorAll('input[name=files]').forEach(i=>i.checked=true)"),
            Button("Select None", type="button", cls=(ButtonT.default, "mr-2"), hx_on_click="document.querySelectorAll('input[name=files]').forEach(i=>i.checked=false)"),
            Button(Loading(cls=(LoadingT.spinner, LoadingT.sm), htmx_indicator=True), "Apply Selection", type="submit", cls=(ButtonT.primary, "ml-auto")),
            cls=("flex items-center")
        ),
        action="/select_files",
        hx_post="/select_files",
        hx_target="body",
        cls="space-y-4"
    )

    content = [
        H3(f"Torrent: {title}"),
        DividerSplit(cls="h-3 mb-2"),
        H6(f"Status: {status}", cls=(TextPresets.muted_sm, "mb-2")),
        P(f"Progress: {progress}") if progress is not None else None,
        select_form,
        Button("Go back", cls=(ButtonT.default, "w-full", "mt-4"), hx_on_click="window.location='/'")
    ]

    content = [c for c in content if c]
    return Container(*content, cls="max-w-xl mx-auto mt-8")