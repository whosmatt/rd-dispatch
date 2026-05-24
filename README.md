# rd-dispatch

## Overview

rd-dispatch is a proxy service that unrestricts and dispatches Real-Debrid downloads via a simple HTTP API and web UI.  
Torrents are supported via magnet links and expose functionality to select files from multi-file torrents.  
While Real-Debrid does not explicitly prohibit this usage, ensure compliance with their [Terms of Service](https://real-debrid.com/terms).

## Installation

This will run the `rd-dispatch` service using Docker Compose.

```yaml
services:
  rd-dispatch:
    image: whosmatt/rd-dispatch:latest
    container_name: rd-dispatch
    restart: unless-stopped
    ports:
      - "5001:5001"
    environment:
      REALDEBRID_TOKEN: TKT...
      DISCORD_TOKEN: ... (optional)
      PUBLIC_BASE_URL: https://rd.example.com (only required for Discord)
      ACCOUNTS: |
        user1:test
        user2:pass
```

### Authentication & Guest links
All endpoints up to the 'Download Ready' page require HTTP Basic Auth. Any valid `username:password` in `ACCOUNTS` is accepted.  
Once you reach a 'Download Ready' page, the URL itself is an encrypted guest link that can be accessed without authentication, valid for 24 hours. It can only be used to download the specific file chosen by the authenticated user.

### Discord Bot
By providing a `DISCORD_TOKEN`, you enable an optional Discord bot that exposes guest link generation via `/unrestrict` as well as `/hosters` to list supported hosters. The commands are usable by anyone by default, so don't forget to set the intended roles/channels in Discord via server settings -> integrations. Torrents are not supported.
The bot needs permissions for slash commands and optionally, embed links. 

#### Setting a static key
Guest links invalidate upon service restart due to the encryption key being rotated.  
If you don't want this, set the environment variable `GUEST_SECRET` to a valid Fernet key:  
`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.

### Deployment
- For public access, use a reverse proxy (e.g., Caddy, Nginx) for SSL and IPv6.
- No persistent storage; all downloads are streamed.

### Notes
- Designed for single-user, low-traffic use.
- Many actions are synchronous.
- Real-Debrid API rate limit of 250 requests/minute applies (but is unlikely to be hit).
- UI built with MonsterUI.