import os

def get_settings():
    token = os.getenv("REALDEBRID_TOKEN")
    if not token:
        raise RuntimeError("REALDEBRID_TOKEN not set in environment.")
    return {"token": token}
