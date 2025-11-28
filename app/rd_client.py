
import httpx
from config import settings

class RDAPI:
    base = "https://api.real-debrid.com/rest/1.0/"
    unrestrict_link = f"{base}unrestrict/link"
    hosts_domains = f"{base}hosts/domains"
    hosts_status = f"{base}hosts/status"

class RDClientError(Exception):
    pass

def unrestrict(url):
    token = settings["token"]
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = httpx.post(RDAPI.unrestrict_link, data={"link": url}, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "download" not in data or "filename" not in data:
            raise RDClientError("Invalid response from Real-Debrid.")
        return {"filename": data["filename"], "download_url": data["download"]}
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Real-Debrid error: {e.response.text}")
    except Exception as e:
        raise RDClientError(str(e))

def supported_hosts():
    try:
        token = settings["token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = httpx.get(RDAPI.hosts_status, timeout=10, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        hosts = []
        for domain, info in data.items():
            # skip unsupported hosts
            if info.get("supported") != 1:
                continue
            status = info.get("status")
            hosts.append({
                "domain": domain,
                "name": info.get("name") or domain,
                "image": info.get("image"),
                "status": status
            })
        return hosts
    except Exception as e:
        raise RDClientError(str(e))