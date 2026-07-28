from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from core.config import settings
from core.constants import constants
import hashlib

pwd_context = CryptContext(
    schemes=[constants.BCRYPT],
    deprecated=constants.AUTO
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(data: dict) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=float(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload.update({
        constants.EXP: expire,
        constants.TYPE: constants.ACCESS
    })

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get(constants.TYPE) != constants.ACCESS:
            raise JWTError(constants.INVALID_TKN)
        return payload
    
    except JWTError:
        raise JWTError(constants.INVALID_TKN)
    
def create_refresh_token(data: dict) -> tuple[str, datetime]:
    payload = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({
        constants.EXP: exp,
        constants.TYPE: constants.REFRESH
    })
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return token, exp

def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get(constants.TYPE) != constants.REFRESH:
            raise JWTError(constants.INVALID_TKN)
        return payload
    except JWTError:
        raise JWTError(constants.INVALID_TKN)
