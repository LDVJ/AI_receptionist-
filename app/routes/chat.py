from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from .. import schemas, models, gemini_services

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

@router.post("/{slug}", response_model=schemas.AIResponse)
async def get_ai_response(slug : str, question : schemas.QuestionPayload, db : AsyncSession = Depends(get_db)):
    print("==slug==", slug)
    hotel = await db.execute(select(models.Hotel).where(models.Hotel.slug == slug))
    hotel_data = hotel.scalar_one_or_none()

    print("==hotel info==", hotel_data)

    if hotel_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    
    faqs = await db.execute(select(models.HotelFAQ).where(models.HotelFAQ.hotel_id == hotel_data.id))
    faqs_data = faqs.scalars().all()

    answer : str = await gemini_services.get_gemini_response(hotel_data.hotel_name, faq_data=faqs_data, user_question=question)

    return {
        "answer" : answer
    }
