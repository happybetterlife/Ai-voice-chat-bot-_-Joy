import base64, hmac, hashlib, time

def create_token(api_key: str, api_secret: str, identity: str, ttl: int = 3600):
    now = int(time.time())
    payload = f"{identity}|{now+ttl}"
    sig = hmac.new(api_secret.encode(), payload.encode(), hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(f"{api_key}:{payload}:{base64.urlsafe_b64encode(sig).decode()}".encode()).decode()
    return token
