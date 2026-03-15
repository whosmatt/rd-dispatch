from config import settings
from fasthtml.common import Response
import base64
import hmac
import hashlib
import json
import time

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

def generate_guest_token(download_url: str, filename: str) -> str:
    payload = json.dumps({"u": download_url, "f": filename, "exp": int(time.time()) + _GUEST_TOKEN_TTL}, separators=(',', ':')).encode()
    payload_b64 = base64.urlsafe_b64encode(payload).rstrip(b'=').decode()
    sig = hmac.new(settings['guest_secret'].encode(), payload_b64.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b'=').decode()
    return f"{payload_b64}.{sig_b64}"

def verify_guest_token(token: str):
    """Returns (download_url, filename) or raises ValueError."""
    if len(token) > 4096: # Prevent DoS with huge tokens
        raise ValueError("Token too long")
    try:
        payload_b64, sig_b64 = token.rsplit('.', 1)
    except ValueError as e:
        raise ValueError("Invalid token format") from e
    expected_sig = hmac.new(settings['guest_secret'].encode(), payload_b64.encode(), hashlib.sha256).digest()
    expected_b64 = base64.urlsafe_b64encode(expected_sig).rstrip(b'=').decode()
    if not hmac.compare_digest(expected_b64, sig_b64):
        raise ValueError("Token expired or invalid")
    padding = 4 - len(payload_b64) % 4
    payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '=' * (padding % 4)))
    if time.time() > payload['exp']:
        raise ValueError("Link expired")
    return payload['u'], payload['f']
