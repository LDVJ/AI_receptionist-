from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from .. import oauth2, schemas, models, utilities

router =  APIRouter(
    tags=["Hotel"],
    prefix="/admin/hotel"
)

@router.post("/create", response_model=schemas.HotelResponse, status_code=status.HTTP_201_CREATED)
async def create_hotel(payload : schemas.HotelCreate, user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db)):
    gen_slug = utilities.slug_generation(payload.hotel_name)
    gen_id = utilities.generate_id()
    admin = user_info.id
    message  = payload.welcome_msg

    check_slug = await db.execute(select(models.Hotel).where(models.Hotel.slug == gen_slug))
    is_present = check_slug.scalar_one_or_none()

    if is_present:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Slug Already present")
    
    newHotel = models.Hotel(
        id = gen_id,
        hotel_name = payload.hotel_name,
        admin_id = admin,
        welcome_msg = message,
        slug = gen_slug
    )

    db.add(newHotel)
    await db.commit()
    await db.refresh(newHotel)

    return newHotel
    

@router.patch("/update", response_model=schemas.HotelResponse, status_code=status.HTTP_200_OK)
async def update_hotel(payload : schemas.HotelUpdate, user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db)):
    updated_info = payload.model_dump(exclude_unset=True)

    hotel_id = user_info.hotel.id 

    hotel = await db.execute(select(models.Hotel).options(selectinload(models.Hotel.admin)).where(models.Hotel.id == hotel_id))
    hotel_result = hotel.scalar_one_or_none()

    for key, value in updated_info.items():
        setattr(hotel_result, key, value)
    
    await db.commit()
    await db.refresh(hotel_result)

    return hotel_result


@router.get("/dashboard", response_model=schemas.HotelResponse, status_code=status.HTTP_200_OK)
async def get_hotel_info(user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db)):
    hotel_id = user_info.hotel.id

    if hotel_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Hotel Found for this user")

    hotel = await db.execute(select(models.Hotel).where(models.Hotel.id == hotel_id))
    hotel_info = hotel.scalar_one_or_none()

    if hotel_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Hotel Found for this user")
    
    return hotel_info


@router.patch("/{slug}")
async def update_slug(slug : str, payload: str, db : AsyncSession = Depends(get_db), user_info : models.Users = Depends(oauth2.get_user_with_token)):
    hotel_slug = user_info.hotel.slug

    hotel = await db.execute(select(models.Hotel).where(models.Hotel.slug == slug))
    hotel_result = hotel.scalar_one_or_none()

    if hotel_result is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorised Action")

    if hotel_slug != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorised Action")
    
    setattr(hotel_result, "welcome_msg", payload)

    await db.commit()
    await db.refresh(hotel_result)

    return hotel_result