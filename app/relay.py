import httpx

CHUNK_SIZE = 65536  # 64k

def stream_file(download_url):
    try:
        with httpx.stream("GET", download_url, timeout=30) as r:
            r.raise_for_status()
            for chunk in r.iter_bytes(CHUNK_SIZE):
                yield chunk
    except Exception as e:
        raise RuntimeError(f"Failed to stream file: {e}")
