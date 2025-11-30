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
      ACCOUNTS: |
        user1:test
        user2:pass

```
### Authentication
All endpoints require HTTP Basic Auth. Any valid `username:password` in `ACCOUNTS` is accepted.

### Deployment
- For public access, use a reverse proxy (e.g., Caddy, Nginx) for SSL and IPv6.
- No persistent storage; all downloads are streamed.

### Notes
- Designed for single-user, low-traffic use.
- Many actions are synchronous.
- Real-Debrid API rate limit of 250 requests/minute applies (but is unlikely to be hit).
- UI built with MonsterUI.