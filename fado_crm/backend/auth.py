# FADO CRM - JWT Authentication System
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from functools import wraps
from database import get_db
from models import NguoiDung, VaiTro

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fado_crm_super_secret_key_2024_vietnam_rocks")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# HTTP Bearer for token extraction
security = HTTPBearer()

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[NguoiDung]:
    """Authenticate user with email and password"""
    user = db.query(NguoiDung).filter(
        NguoiDung.email == email,
        NguoiDung.is_active == True
    ).first()

    if not user or not verify_password(password, user.mat_khau_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise AuthenticationError()
        return payload
    except JWTError:
        raise AuthenticationError()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> NguoiDung:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)

    # Check token type
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    email = payload.get("sub")
    user = db.query(NguoiDung).filter(
        NguoiDung.email == email,
        NguoiDung.is_active == True
    ).first()

    if user is None:
        raise AuthenticationError()
    return user

def get_current_active_user(
    current_user: NguoiDung = Depends(get_current_user)
) -> NguoiDung:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user

# Admin-only access
def get_admin_user(current_user: NguoiDung = Depends(get_current_active_user)) -> NguoiDung:
    """Get current user if admin"""
    if current_user.vai_tro != VaiTro.ADMIN:
        raise AuthorizationError("Admin access required")
    return current_user

# Manager or Admin access
def get_manager_user(current_user: NguoiDung = Depends(get_current_active_user)) -> NguoiDung:
    """Get current user if manager or admin"""
    if current_user.vai_tro not in [VaiTro.ADMIN, VaiTro.MANAGER]:
        raise AuthorizationError("Manager or Admin access required")
    return current_user

# Login function
def login_user(db: Session, email: str, password: str) -> dict:
    """Login user and return tokens"""
    user = authenticate_user(db, email, password)
    if not user:
        raise AuthenticationError("Incorrect email or password")

    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.vai_tro.value},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.vai_tro.value}
    )

    # Update last login
    user.lan_dang_nhap_cuoi = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "ho_ten": user.ho_ten,
            "vai_tro": user.vai_tro.value,
            "is_active": user.is_active,
            "ngay_tao": user.ngay_tao,
            "lan_dang_nhap_cuoi": user.lan_dang_nhap_cuoi
        }
    }