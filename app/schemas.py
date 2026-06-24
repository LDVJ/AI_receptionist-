from pydantic import BaseModel, EmailStr
from datetime import datetime
from .constants.status import FAQStatus

class TokenData(BaseModel):
    id : str

class UserSignUp(BaseModel):
    email : EmailStr
    password : str
    name  : str

class HotelFAQCreate(BaseModel):
    question : str
    answer : str
    category : str

class HotelFAQResponse(HotelFAQCreate):
    id: str
    hotel_id : str
    created_at : datetime

    model_config = {
        "from_attributes":True
    }


class HotelCreate(BaseModel):
    hotel_name : str
    welcome_msg : str | None = None

class HotelUpdate(BaseModel):
    hotel_name : str | None = None
    welcome_msg : str | None = None

    
class HotelResponse(HotelCreate):
    id: str
    slug : str
    created_at : datetime

    
    model_config = {
        "from_attributes":True
    }


class UserResponse(BaseModel):
    id : str
    email : EmailStr
    name : str
    created_at: datetime

    
    model_config = {
        "from_attributes":True
    }

class ConversationCreate(BaseModel):
    hotel_id : str
    guest_question : str
    ai_response : str
    was_answerable : bool | None = True

class ConversationResponse(ConversationCreate):
    id : int
    created_at : datetime

    
    model_config = {
        "from_attributes":True
    }

class UnansweredQuestCreate(BaseModel):
    conversation_id : str
    status : FAQStatus | None = FAQStatus.PENDING

class UnansweredQuestResponse(UnansweredQuestCreate):
    id : str
    created_at : datetime

    
    model_config = {
        "from_attributes":True
    }

# Relationship Schemas

class UnansweredQuestConversationRel(UnansweredQuestResponse):
    conversation : ConversationResponse

class ConversationUnansweredRel(ConversationResponse):
    unanswered_entry : UnansweredQuestResponse

class ConversationHotelRel(ConversationResponse):
    hotel : HotelResponse

class UserHotelRel(UserResponse):
    hotel : HotelResponse

class HotelAdminRel(HotelResponse):
    admin : UserResponse

class HotelFAQRel(HotelResponse):
    faqs : list[HotelFAQResponse]

class HotelConversationRel(HotelResponse):
    conversation : list[ConversationResponse]

class FAQHotelRel(HotelFAQResponse):
    hotel : HotelResponse