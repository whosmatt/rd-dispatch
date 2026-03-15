import os
import secrets

def get_settings():
    token = os.getenv("REALDEBRID_TOKEN")
    if not token:
        raise RuntimeError("REALDEBRID_TOKEN not set in environment.")
    accounts_raw = os.getenv("ACCOUNTS", "")
    accounts = set()
    for line in accounts_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            accounts.add(line)
    guest_secret = os.getenv("GUEST_SECRET") or secrets.token_hex(32)
    return {"token": token, "accounts": accounts, "guest_secret": guest_secret}

settings = get_settings()