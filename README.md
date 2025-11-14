# rd-dispatch

## Overview

rd-dispatch is a proxy service that unrestricts and dispatches Real-Debrid downloads via a simple HTTP API and web UI.  
Torrents are not currently supported.

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
- Designed for few-user, low-traffic use.
- UI built with MonsterUI.