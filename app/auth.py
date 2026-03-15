from config import settings
from fasthtml.common import Response
import base64
import json
import time
from cryptography.fernet import Fernet, InvalidToken

def check_auth(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Basic '):
        return False
    try:
        creds = base64.b64decode(auth.split(' ', 1)[1]).decode()
    except Exception:
        return False
    return creds in settings['accounts']

def require_auth(request):
    if not check_auth(request):
        return Response(
            "Unauthorized", status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Login Required"'}
        )

_GUEST_TOKEN_TTL = 24 * 60 * 60  # 24 hours
_FERNET = Fernet(settings['guest_secret'].encode())

def generate_guest_token(download_url: str, filename: str) -> str:
    payload = json.dumps({"u": download_url, "f": filename, "exp": int(time.time()) + _GUEST_TOKEN_TTL}, separators=(',', ':')).encode()
    return _FERNET.encrypt(payload).decode()

def verify_guest_token(token: str):
    """Returns (download_url, filename) or raises ValueError."""
    if len(token) > 8192: # Prevent DoS with huge tokens
        raise ValueError("Token too long")
    try:
        payload = json.loads(_FERNET.decrypt(token.encode(), ttl=_GUEST_TOKEN_TTL))
    except (InvalidToken, json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise ValueError("Token expired or invalid") from exc
    if time.time() > payload['exp']:
        raise ValueError("Link expired")
    return payload['u'], payload['f'], payload['exp']
