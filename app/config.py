import os
from cryptography.fernet import Fernet

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
    guest_secret = os.getenv("GUEST_SECRET") or Fernet.generate_key().decode()
    return {"token": token, "accounts": accounts, "guest_secret": guest_secret}

settings = get_settings()