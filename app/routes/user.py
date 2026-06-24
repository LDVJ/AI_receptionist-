from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from .. import schemas
from .. import models
from sqlalchemy.engine import Result
from .. import utilities


router = APIRouter(
    tags=["signup"],
)

@router.post("/admin/signup", response_model=schemas.UserResponse)
async def signup(payload : schemas.UserSignUp, db : AsyncSession = Depends(get_db)):
    check_user = await db.execute(select(models.Users).where(models.Users.email == payload.email))
    result : Result = check_user.scalar_one_or_none()
    if result is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User Already exist")
    
    hashed_password =  utilities.create_hash_password(payload.password)
    user_id = utilities.generate_id()

    new_user  = models.Users(
        id = user_id,
        name = payload.name,
        email = payload.email,
        hash_password = hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
