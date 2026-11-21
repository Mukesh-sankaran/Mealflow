
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import settings


# Choose bcrypt for securely hashing passwords
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# Convert a normal password into a secure hash
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Check whether the entered password matches the saved hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Create a JWT token after successful login
def create_access_token(data: dict) -> str:
    token_data = data.copy()

    # Set the time when the token should expire
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_data.update({"exp": expire})

    # Sign the token using our secret key
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


# Check whether a JWT token is valid
def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        return payload

    except JWTError:
        return None
