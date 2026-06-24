from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .. import schemas, models, oauth2, services
from ..db import get_db

router = APIRouter(
    tags=["faqs"],
    prefix="/admin/hotel/faqs"
)

@router.post("/create/single", response_model=schemas.HotelFAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(payload : schemas.HotelFAQCreate, user_info : models.Users = Depends(oauth2.get_user_with_token) , db : AsyncSession = Depends(get_db)):
    hotel_id = user_info.hotel.id

    if hotel_id is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,  detail="Hotel Not Found")
    
    new_faq = await services.create_single_faq(faq_data=payload, user_info=user_info, db =  db)

    return new_faq

@router.post("/create/bulk", response_model=list[schemas.HotelFAQResponse], status_code=status.HTTP_201_CREATED)
async def create_all_faq(payload : list[schemas.HotelFAQCreate], user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db) ):
    for data in payload:
        await services.create_single_faq(faq_data=data, user_info=user_info, db = db)
    
    hotel_id = user_info.hotel.id

    all_faqs = await db.execute(select(models.HotelFAQ).where(models.HotelFAQ.hotel_id == hotel_id))
    all_faqs_data = all_faqs.scalars().all()

    return all_faqs_data