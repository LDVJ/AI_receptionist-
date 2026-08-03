from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, oauth2, models
from ..db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(
    tags=["Unanswered"],
    prefix="/hotel/unanswered"
)

@router.get("/",response_model=list[schemas.ConversationUnansweredRel], status_code = status.HTTP_200_OK)
async def get_all_unanswered_quest(user_info : models.Users = Depends(oauth2.get_user_with_token), db : AsyncSession  = Depends(get_db)):

    hotel = await db.execute(select(models.Hotel).where(models.Hotel.admin_id == user_info.id))
    hotel_info = hotel.scalar_one_or_none()

    if hotel_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Hotel Not found")

    conversations = await db.execute(select(models.Conversations).options(selectinload(models.Conversations.unanswered_entry)).where(models.Conversations.hotel_id == user_info.hotel.id).where(models.Conversations.was_answerable == False))
    conversations_info = conversations.scalars().all()

    if conversations_info is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Hotel of The user not found")

    return conversations_info


@router.patch("/{id}", response_model=schemas.UnansweredQuestConversationRel, status_code=status.HTTP_200_OK)
async def status_update(id : str, question_status : schemas.StatusUpdate, db : AsyncSession = Depends(get_db), user_info : models.Users = Depends(oauth2.get_user_with_token)):
    conversation_unanswered = await db.execute(select(models.UnansweredQuestions).join(models.Conversations, models.UnansweredQuestions.conversation_id == models.Conversations.id).options(selectinload(models.UnansweredQuestions.conversation)).where(models.UnansweredQuestions.id == id, models.Conversations.hotel_id == user_info.hotel.id))
    conversation_unanswered_info = conversation_unanswered.scalar_one_or_none()
    
    if conversation_unanswered_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation Not Found")

    

    conversation_unanswered_info.status = question_status.status

    await db.commit()
    await db.refresh(conversation_unanswered_info)

    return conversation_unanswered_info