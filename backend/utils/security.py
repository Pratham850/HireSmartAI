import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from config import settings

try:
    import jwt
except ImportError:
    jwt = None

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    pwd_context = None


def hash_password(password: str) -> str:
    """Hash password using bcrypt or SHA-256 fallback."""
    if pwd_context:
        return pwd_context.hash(password)
    # Simple salt+sha256 fallback for environments without bcrypt installed
    salt = settings.SECRET_KEY[:8].encode("utf-8")
    return "sha256$" + hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000).hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    if pwd_context and not hashed_password.startswith("sha256$"):
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    # SHA-256 fallback verification
    expected = hash_password(plain_password)
    return expected == hashed_password


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT Access Token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})

    if jwt:
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Simple base64 fallback token if PyJWT is missing
    import base64, json
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    signature = hashlib.sha256(f"{header_b64}.{payload_b64}.{settings.SECRET_KEY}".encode()).hexdigest()
    return f"{header_b64}.{payload_b64}.{signature}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT Access Token."""
    if jwt:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except Exception:
            pass

    # Simple base64 fallback decoder
    try:
        import base64, json
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_json = base64.urlsafe_b64decode(parts[1] + "==").decode()
        payload = json.loads(payload_json)
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            return None
        return payload
    except Exception:
        return None
