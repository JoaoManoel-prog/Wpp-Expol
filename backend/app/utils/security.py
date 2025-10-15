import os, hmac, hashlib, time
from typing import Optional
from jose import jwt

def verify_meta_signature(app_secret: str, body: bytes, signature_header: Optional[str]) -> bool:
    if not signature_header or "=" not in signature_header:
        return False
    _, received_hash = signature_header.split("=", 1)
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(received_hash, expected)

def create_jwt(secret: str, subject: str, expire_minutes: int = 60*24*30):
    payload = {"sub": subject, "exp": int(time.time()) + expire_minutes*60}
    return jwt.encode(payload, secret, algorithm="HS256")
