import os

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
    return {"token": token, "accounts": accounts}
