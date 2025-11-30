from monsterui.franken import *
from urllib.parse import quote_plus
from monsterui.daisy import Loading, LoadingT, Toast, ToastVT, ToastHT
from monsterui.franken import P, A, Ul, Li, Img, Div, Span

def _human_size(num):
    # simple human-readable size
    try:
        num = int(num)
    except Exception:
        return ""
    for unit in ["B", "KB", "MB", "GB", "TB (good luck!)"]:
        if num < 1024:
            return f"{num}{unit}"
        num = num // 1024
    return f"{num}PB (how????)"

def _error_toast(message):
    return Toast(
        message,
        dur=10,
        cls=[ToastVT.bottom, ToastHT.center],
        alert_cls="text-white bg-red-500 border-red-500"
    )

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
        method="get",
        hx_get="/convert",
        hx_target="body"
    )
    content = [
        H3(A("rd-dispatch", href="https://github.com/whosmatt/rd-dispatch")),
        DividerSplit(cls="h-3 mb-2"),
        H6("Download any link ", A("supported", href="/hosts", cls=(AT.primary)), " by Real-Debrid. Torrents are supported via magnet links.", cls=(TextPresets.muted_sm, "mb-4")),
        form,
        _error_toast(error) if error else None
    ]
    container = Container(*content, cls="max-w-xl mx-auto mt-8")
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


def render_torrent(info, error=None):
    # This function is a bit convoluted due to real-debrid stuffing a lot of functionality into this endpoint
    title = info.get("original_filename") or info.get("filename") or info.get("id")
    status = info.get("status")
    progress = info.get("progress")
    files = info.get("files") or []
    links = info.get("links")
    seeders = info.get("seeders")
    speed = info.get("speed")

    items = []
    for f in files:
        fid = f.get("id")
        path = f.get("path")
        size = f.get("bytes")
        selected = f.get("selected")
        readable = _human_size(size)
        checkbox = LabelCheckboxX(f"{path} ({readable})", id=f"file_{fid}", name="files", value=str(fid), checked=bool(selected))
        items.append(Li(checkbox))

    file_list = Ul(*items, cls=ListT.striped) if items else P("No files yet")

    select_form = Form(
        Input(type="hidden", name="torrent_id", value=info.get("id")),
        file_list,
        Div(
            Button("Select All", type="button", cls=(ButtonT.secondary, "mr-2"), hx_on_click="document.querySelectorAll('input[name=files]').forEach(i=>i.checked=true)"),
            Button("Select None", type="button", cls=(ButtonT.default, "mr-2"), hx_on_click="document.querySelectorAll('input[name=files]').forEach(i=>i.checked=false)"),
            Button(Loading(cls=(LoadingT.spinner, LoadingT.sm), htmx_indicator=True),"Generate Links", type="submit", cls=(ButtonT.primary, "ml-auto", "disabled:opacity-60"),
                disabled=(str(status or "").lower() != "waiting_files_selection")),
            cls=("flex items-center")
        ),
        action="/select_files",
        hx_post="/select_files",
        hx_target="body",
        onsubmit="if(document.querySelectorAll('input[name=files]:checked').length===0){ event.preventDefault(); event.stopImmediatePropagation(); alert('Please select at least one file'); return false;} return true;",
        cls="space-y-4"
    )

    content = [
        H3(f"Torrent: {title}"),
        DividerSplit(cls="h-3 mb-2"),
        H6(f"Status: {status}", cls=(TextPresets.muted_sm, "mb-2")),
        P(f"Progress: {progress}%") if progress is not None else None,
        P(f"Seeders: {seeders}") if seeders is not None else None,
        P(f"Speed: {_human_size(speed)}/s") if speed is not None else None,
        select_form,
        DividerSplit(cls="h-3 mb-2"),
        _error_toast(error) if error else None
    ]

    # If Real-Debrid returned host links, show forms to unrestrict each link
    if links:
        link_items = []
        for l in links:
            encoded = quote_plus(l)
            link_href = f"/convert?url={encoded}"
            link_items.append(Li(A(l, href=link_href, target="_blank", rel="noopener", cls=AT.primary)))
        links_list = Ul(*link_items, cls=ListT.striped)
        content.extend([H5("Download Links"), links_list])

    content.append(Button("Go back", cls=(ButtonT.default, "w-full", "mt-4"), hx_on_click="window.location='/'"))

    container = Container(*content, cls="max-w-xl mx-auto mt-8")

    if status in ("queued", "downloading"):
        # Use HTMX to poll the torrent fragment every 5s and swap the outerHTML
        tid = info.get("id") or ''
        wrapper = Div(id=f"torrent-{tid}", hx_get=f"/torrent_info?torrent_id={tid}", hx_trigger="every 5s", hx_swap="outerHTML", hx_target="this")
        return wrapper(container)

    return container
