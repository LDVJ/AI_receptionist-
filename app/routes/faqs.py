from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, delete
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
    new_faq = await services.create_single_faq(faq_data=payload, user_info=user_info, db =  db)

    return new_faq

@router.post("/create/bulk", response_model=list[schemas.HotelFAQResponse], status_code=status.HTTP_201_CREATED)
async def create_all_faq(payload : list[schemas.HotelFAQCreate], user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db) ):
    created_faqs = []
    for data in payload:
        new_faq = await services.create_single_faq(faq_data=data, user_info=user_info, db = db)
        created_faqs.append(new_faq)

    return created_faqs


@router.patch("/update/{faq_id}", response_model=schemas.HotelFAQResponse, status_code=status.HTTP_200_OK)
async def update_faq(faq_id : str, payload : schemas.HotelFAQUpdate, user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db)):
    update_data = payload.model_dump(exclude_unset= True)

    faq_data = await db.execute(select(models.HotelFAQ).where(models.HotelFAQ.id == faq_id, models.HotelFAQ.hotel_id == user_info.hotel.id))
    faq_data_result = faq_data.scalar_one_or_none()

    if faq_data_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "FAQ Not Found")

    for key, value in update_data.items():
        setattr(faq_data_result, key, value)
    
    await db.commit()
    await db.refresh(faq_data_result)

    return faq_data_result

@router.delete("/delete/{faq_id}", status_code=status.HTTP_200_OK)
async def delete_faq(faq_id : str, user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db)):
    
    faq_to_delete = delete(models.HotelFAQ).where(models.HotelFAQ.id  == faq_id, models.HotelFAQ.hotel_id == user_info.hotel.id)

    result = await db.execute(faq_to_delete)

    if result.rowcount == 0:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Faq Not Found")

    await db.commit()
    
    return {
        "message":"FAQ Deleted Successfully"
    }


@router.get("/", response_model=list[schemas.HotelFAQResponse], status_code= status.HTTP_200_OK)
async def get_all_faqs(user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession = Depends(get_db)):
    all_Faqs = await db.execute(select(models.HotelFAQ).where(models.HotelFAQ.hotel_id == user_info.hotel.id))
    all_Faqs_data = all_Faqs.scalars().all()

    if not all_Faqs_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No Faq Found")
    
    return all_Faqs_data