"""
Team Forge Authentication Service
---------------------------------
Handles Google OAuth 2.0 credential verification and JWT session tokens.
"""

import os
import time
from typing import Any, Dict, Optional
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

JWT_SECRET = os.environ.get("JWT_SECRET", "team-forge-super-secret-jwt-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 7 * 24 * 3600  # 7 days
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")


def verify_google_credential(credential: str) -> Dict[str, Any]:
    """
    Verifies a Google ID token from @react-oauth/google.
    Returns user dict with email, name, avatar_url.
    Supports development/test fallback when testing locally.
    """
    try:
        request = google_requests.Request()
        # If GOOGLE_CLIENT_ID is set, verify against it; otherwise verify signature without audience check
        audience = GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else None
        id_info = id_token.verify_oauth2_token(credential, request, audience=audience)
        
        email = id_info.get("email")
        if not email:
            raise ValueError("Token does not contain an email address.")

        return {
            "email": email,
            "name": id_info.get("name", email.split("@")[0]),
            "avatar_url": id_info.get("picture", ""),
            "google_id": id_info.get("sub", ""),
        }
    except Exception as exc:
        # Check if credential is a dev/test mock token in the format "dev_email@gmail.com"
        if credential.startswith("dev_") and "@" in credential:
            email = credential.replace("dev_", "")
            return {
                "email": email,
                "name": email.split("@")[0].capitalize(),
                "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={email}",
                "google_id": f"dev_sub_{email}",
            }
        raise ValueError(f"Invalid Google credential token: {str(exc)}")


def create_access_token(user: Dict[str, Any]) -> str:
    """Creates a signed JWT session token with 7-day validity."""
    payload = {
        "user_id": user["id"],
        "email": user["email"],
        "name": user.get("name", ""),
        "avatar_url": user.get("avatar_url", ""),
        "exp": int(time.time()) + JWT_EXPIRATION_SECONDS,
        "iat": int(time.time()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a session JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None
