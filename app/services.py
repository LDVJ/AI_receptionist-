from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas, utilities

async def create_single_faq(faq_data : schemas.HotelFAQCreate, user_info : models.Users, db : AsyncSession):
    new_faq= models.HotelFAQ(
        id = utilities.generate_id(),
        hotel_id = user_info.hotel.id,
        question = faq_data.question,
        answer = faq_data.answer,
        category = faq_data.category
    )

    db.add(new_faq)
    await db.commit()
    await db.refresh(new_faq)

    return new_faq
