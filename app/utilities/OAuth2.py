from jose import jwt, JWTError, ExpiredSignatureError
from app.config import settings
from datetime import datetime, timedelta
from app import schemas, models
from fastapi import HTTPException, status,Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db

ouath_schema=OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(pwd_plain: str, pwd_hashed: str):
    return pwd_context.verify(pwd_plain, pwd_hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def verif_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id = payload.get("id")
        token_data = schemas.PayloadData(id=id)
        return token_data
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except JWTError:
        raise credentials_exception


def get_current_admin(db:Session = Depends(get_db), token:str = Depends(ouath_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verif_access_token(token, credentials_exception)
    admin = db.query(models.Admin).filter(models.Admin.id  == token_data.id).first()
    return admin