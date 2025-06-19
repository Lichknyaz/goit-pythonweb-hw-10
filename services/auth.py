from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from settings.base import HASH_ALGORITHM, HASH_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from data_base.connect import get_db
from data_base.models import User
import bcrypt
from typing import Optional

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return hash_password(password)

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, HASH_SECRET, algorithm=HASH_ALGORITHM)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating access token"
        )

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(token.credentials, HASH_SECRET, algorithms=[HASH_ALGORITHM])

        email: str = payload.get("sub")
        if email is None:
            print("No 'sub' claim found in token")
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"No user found for email: {email}")
            raise credentials_exception

        return user

    except JWTError as e:
        print(f"JWT decode error: {str(e)}")
        raise credentials_exception
