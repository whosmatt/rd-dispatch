from config import settings
from fasthtml.common import Response
import base64

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
