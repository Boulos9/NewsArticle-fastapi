"""
    will handle the authorization.
    check if the same user who logged in is the one who
    are making requests. JWT
    we need a SEKRET_KEY, and an ALGORITHM to create the signiture
"""
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import get_settings

settings = get_settings()


# dependency to check if user is authenticated
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm 
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_expire


def create_access_token(data: dict): # created when user logged in
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # PAYLOAD
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt # SIGNATURE


def verify_access_token(token: str, credentials_exceptions, sk: str = SECRET_KEY):
    try:
        payload = jwt.decode(token, sk, algorithms=ALGORITHM)
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exceptions
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exceptions

    return token_data

# will be used as dependency to verify if the user making requests is the same autherized current_user 
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                            detail=f"Could not validate credentials",
                                            headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    if user is None:
        raise credentials_exception

    return user