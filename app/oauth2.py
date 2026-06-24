# generate token
from config import settings
from fastapi.security import oauth2
from fastapi import Depends, HTTPException, status
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from .schemas import TokenData
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db
import models

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXP_TIME_HOURS = settings.ACCESS_TOKEN_EXP_TIME_HOURS

oauth2_schema = oauth2.OAuth2PasswordBearer(tokenUrl="/login")

def create_jwt_token(data : dict) -> str:
    copy_data = deepcopy(data)
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXP_TIME_HOURS)
    copy_data.update({"exp":expire})
    encoded_jwt = jwt.encode(claims = copy_data, key=SECRET_KEY, algorithm=ALGORITHM)

    return {
        encoded_jwt
    }

def verify_jwt_token(token : str, credentials_exception):
    try:
        decoded_data = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        token_data : str = decoded_data.get("user_id")
        if token_data is None:
            raise credentials_exception
        user_data = TokenData(id = token_data)

    except JWTError:
        raise credentials_exception
    
    return user_data

async def get_user_with_token(bearer_token : str = Depends(oauth2_schema), db : AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorised Access",
        headers={"WWW-Authenticate":"Bearer"}
    )

    token = verify_jwt_token(token=bearer_token, credentials_exception=credentials_exception)

    result = await db.execute(select(models.Users).where(models.Users.id == token.id))

    user_data = result.scalar_one_or_none()

    return user_data
