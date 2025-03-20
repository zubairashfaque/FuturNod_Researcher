# API authentication module
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from api.config import SECURITY_CONFIG

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Define a user model for authentication
class User(BaseModel):
    """User model for authentication"""
    username: str
    disabled: Optional[bool] = None


# Get admin credentials from environment variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")

# If no hash is provided, generate one from default password
if not ADMIN_PASSWORD_HASH:
    default_password = os.getenv("ADMIN_PASSWORD", "adminpassword")
    ADMIN_PASSWORD_HASH = pwd_context.hash(default_password)
    logger.warning("Using default admin password. Please set ADMIN_PASSWORD_HASH in .env for production.")

# User database constructed from environment variables
USERS_DB = {
    ADMIN_USERNAME: {
        "username": ADMIN_USERNAME,
        "hashed_password": ADMIN_PASSWORD_HASH,
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get hash of a password"""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get a user from the database"""
    if username in USERS_DB:
        user_dict = USERS_DB[username]
        return user_dict
    return None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SECURITY_CONFIG["access_token_expire_minutes"])

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECURITY_CONFIG["secret_key"],
        algorithm=SECURITY_CONFIG["algorithm"]
    )

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECURITY_CONFIG["secret_key"],
            algorithms=[SECURITY_CONFIG["algorithm"]]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception

    return User(**user)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
