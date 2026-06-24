from fastapi import APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from ..db import get_db
from sqlalchemy.ext.asyncio import  AsyncSession
from sqlalchemy import select
from .. import oauth2
from .. import models
from .. import utilities


router = APIRouter(
    tags=["login"]
)

@router.post("/admin/login")
async def login(user_cred : OAuth2PasswordRequestForm = Depends(), db : AsyncSession = Depends(get_db)):
    check_user = await db.execute(select(models.Users).where(models.Users.email == user_cred.username))
    result = check_user.scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not found")
    
    str_password = user_cred.password
    hash_password = result.hash_password

    isValidPassword = utilities.verify_hash_password(original=str_password, hash_pwd=hash_password)

    if not isValidPassword:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not found")

    user_dict = {
        "user_id" : result.id
    }

    token = oauth2.create_jwt_token(data=user_dict)

    return  {
        "access_token" : token,
        "token_type" : "bearer"
    }

   