
import httpx
from config import settings


class RDClientError(Exception):
    pass


class RDClient:
    base = "https://api.real-debrid.com/rest/1.0/"

    def __init__(self, token=None):
        # Prefer explicit token, otherwise read from config settings
        self.token = token if token is not None else settings.get("token") if isinstance(settings, dict) else settings["token"]
        if not self.token:
            raise RDClientError("Real-Debrid token not configured in settings.")

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @property
    def unrestrict_link(self):
        return f"{self.base}unrestrict/link"

    @property
    def hosts_status(self):
        return f"{self.base}hosts/status"

    @property
    def torrents_add_magnet(self):
        return f"{self.base}torrents/addMagnet"

    @property
    def torrents_select_files(self):
        return f"{self.base}torrents/selectFiles/"

    def unrestrict(self, url):
        """Unrestrict a download link and return dict with filename and download_url."""
        try:
            resp = httpx.post(self.unrestrict_link, data={"link": url}, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if "download" not in data or "filename" not in data:
                raise RDClientError("Invalid response from Real-Debrid.")
            return {"filename": data["filename"], "download_url": data["download"]}
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Real-Debrid error: {e.response.text}")
        except Exception as e:
            raise RDClientError(str(e))

    def supported_hosts(self):
        """Return a list of supported hosts with their status."""
        try:
            resp = httpx.get(self.hosts_status, timeout=10, headers=self.headers)
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

    def add_torrent(self, url):
        """Post a magnet link to Real-Debrid and return torrent info (if available).

        Returns the torrent info JSON (from /torrents/info/{id}) when the API
        returns an `id` or `uri` in the addMagnet response. Otherwise raises
        ValueError with the raw response.
        """
        try:
            resp = httpx.post(self.torrents_add_magnet, data={"magnet": url}, headers={**self.headers, "Content-Type": "application/x-www-form-urlencoded"}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            torrent_uri = None
            if isinstance(data, dict):
                torrent_uri = data.get("uri")
                torrent_id = data.get("id")

            if torrent_uri:
                info_resp = httpx.get(torrent_uri, headers=self.headers, timeout=10)
                info_resp.raise_for_status()
                return info_resp.json()

            raise ValueError(f"Real-Debrid response: {data}")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Real-Debrid torrent error: {e.response.text}")
        except Exception as e:
            raise RDClientError(str(e))

    def select_files(self, torrent_id, files):
        """Select files for a given torrent and return updated torrent info.

        `files` may be the string "all" or an iterable of file ids.
        """
        try:
            if files == "all":
                files_param = "all"
            else:
                cleaned = [f for f in files if f is not None and str(f).strip() != ""]
                if not cleaned:
                    raise ValueError("No files selected")
                files_param = ",".join(str(int(f)) for f in cleaned)

            select_url = f"{self.torrents_select_files}{torrent_id}"
            resp = httpx.post(select_url, data={"files": files_param}, headers={**self.headers, "Content-Type": "application/x-www-form-urlencoded"}, timeout=10)
            resp.raise_for_status()

            info_url = f"{self.base}torrents/info/{torrent_id}"
            info_resp = httpx.get(info_url, headers=self.headers, timeout=10)
            info_resp.raise_for_status()
            return info_resp.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Real-Debrid selectFiles error: {e.response.text}")
        except Exception as e:
            raise RDClientError(str(e))
