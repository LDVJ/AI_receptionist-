from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from .. import schemas, models

router = APIRouter(
    tags=["chat"],
    prefix="/chat"
)

@router.get("/{slug}", response_model=schemas.WelcomeResponse, status_code=status.HTTP_200_OK)
async def first_response(slug : str, db : AsyncSession = Depends(get_db)):
    check_hotel = await db.execute(select(models.Hotel).options(selectinload(models.Hotel.faqs)).where(models.Hotel.slug == slug))
    check_hotel_data = check_hotel.scalar_one_or_none()
    
    if check_hotel_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel Not Found")
    
    welcome_msg = check_hotel_data.welcome_msg

    hotel_faqs= check_hotel_data.faqs

    if welcome_msg == None:
        welcome_msg = f"Welcome to {check_hotel_data.hotel_name} chat. How May I help you?"

    return{
        "slug" : slug,
        "welcome_msg" : welcome_msg,
        "faqs" : hotel_faqs
    }
