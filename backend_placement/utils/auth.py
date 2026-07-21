"""
utils/auth.py
─────────────
JWT helpers and the FastAPI dependencies for authentication.
"""

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Request, Response
import os
import jwt
import uuid
import datetime
import secrets
import redis as redis_lib
import pytz
from typing import Optional, List

from database import User, RefreshToken

security = HTTPBearer(auto_error=False)

# ─────────────────────────────────────────────────────────────────────────────
# Redis client — lazy-initialized on first use
# ─────────────────────────────────────────────────────────────────────────────
_redis = None

def get_redis():
    global _redis
    if _redis is None:
        url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        _redis = redis_lib.from_url(url, decode_responses=True)
    return _redis


# ─────────────────────────────────────────────────────────────────────────────
# Token generation
# ─────────────────────────────────────────────────────────────────────────────
def generate_access_token(user_id, role):
    """
    Create a short-lived JWT (15 minutes).
    Includes a unique 'jti' so the token can be individually revoked.
    """
    payload = {
        'user_id': str(user_id),
        'role':    role,
        'jti':     str(uuid.uuid4()),
        'exp':     datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }
    secret_key = os.environ.get('JWT_SECRET_KEY', 'dev_secret')
    return jwt.encode(payload, secret_key, algorithm='HS256')


def generate_refresh_token(user_id, db):
    """Create a long-lived opaque token, save it to DB, return the token string."""
    token      = secrets.token_hex(32)
    ist_now    = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
    expires_at = ist_now + datetime.timedelta(days=7)

    record = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(record)
    db.commit()
    return token


def set_refresh_cookie(response: Response, refresh_token: str):
    """Attach the refresh token as an HTTP-only cookie to a response."""
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        samesite='strict',
        max_age=7 * 24 * 60 * 60   # 7 days
    )
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Redis revocation helpers
# ─────────────────────────────────────────────────────────────────────────────
ACCESS_TOKEN_TTL = 15 * 60   # 15 minutes in seconds

def revoke_access_token(jti):
    """Add a JTI to the Redis blocklist."""
    get_redis().setex(f'blocked_jti:{jti}', ACCESS_TOKEN_TTL, '1')

def block_user(user_id):
    """Block all API access for a user for the next 15 minutes via Redis."""
    get_redis().setex(f'blocked_user:{user_id}', ACCESS_TOKEN_TTL, '1')

def unblock_user(user_id):
    """Remove the Redis block when a user is re-activated."""
    get_redis().delete(f'blocked_user:{user_id}')


# ─────────────────────────────────────────────────────────────────────────────
# Auth dependencies
# ─────────────────────────────────────────────────────────────────────────────
class RequireAuth:
    """
    FastAPI dependency that validates the JWT.
    Usage:
        def my_route(user = Depends(RequireAuth(['student', 'admin']))):
            user_id = user['user_id']
    """
    def __init__(self, roles: List[str] = None):
        self.roles = roles or []

    def __call__(self, request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
        token = None
        if credentials:
            token = credentials.credentials
        elif request.query_params.get('token'):
            token = request.query_params.get('token')
            
        if not token:
            raise HTTPException(status_code=401, detail="Authorization header missing or malformed")

        try:
            secret_key = os.environ.get('JWT_SECRET_KEY', 'dev_secret')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Access token expired. Please refresh.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid access token")

        jti     = payload.get('jti')
        user_id = payload.get('user_id')
        role    = payload.get('role')

        if jti and get_redis().exists(f'blocked_jti:{jti}'):
            raise HTTPException(status_code=401, detail="Token has been revoked. Please login again.")

        if get_redis().exists(f'blocked_user:{user_id}'):
            raise HTTPException(status_code=403, detail="Your account has been deactivated")

        if self.roles and role not in self.roles:
            raise HTTPException(status_code=403, detail="You do not have permission to access this resource")

        return {
            "user_id": user_id,
            "role": role,
            "jti": jti
        }

# Pre-defined dependencies for convenience
require_any_auth = RequireAuth()
require_student = RequireAuth(['student'])
require_company = RequireAuth(['company'])
require_admin = RequireAuth(['admin'])
