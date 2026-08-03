from google import genai
from google.genai import errors as geniai_errors
from .config import settings
from . import schemas, models
import json, asyncio


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

dummy_response_test_1 = {
    "answered" : True,
    "message" : "HEllo Question received"
}
dummy_response_test_2 = {
    "answered" : False,
    "message" : "answer not given"
}

max_tries = 5

async def get_gemini_response(hotel_name: str, faq_data : list[models.HotelFAQ], user_question : schemas.QuestionPayload):

    faq_list = [
    {
        "question": faq.question,
        "answer": faq.answer,
        "category": faq.category,
    }
    for faq in faq_data
    ]

    prompt = f"""
    You are an AI receptionist for "{hotel_name}".

    Your job is to answer customer questions ONLY using the hotel FAQ information provided below.

    Rules:
    1. Never make up hotel information.
    2. If the answer exists in the FAQs, answer naturally and politely.
    3. If the answer is NOT available in the FAQs, politely reply:
    "I'm sorry, I couldn't find that information. Please contact the hotel reception for further assistance."
    4. Do not mention that you are reading FAQs.
    5. Keep answers concise and professional.
    6. If multiple FAQs are relevant, combine their information into one response.
    7. if the question is just generic which don't require hotel Faq data you respond it cleanly(ex - for "hello" -> you can say "how can i help you")
    8. If garbage questions are asked -- politely handle it and ask for something else.


    Hotel FAQs:

    {faq_list}

    Customer Question:

    {user_question.question}
    """
    for attempt in range(max_tries):
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type" : "application/json",
                    "response_schema" : {
                        "type" : "object",
                        "properties" : {
                            "answered":{
                                "type": "boolean"
                            },
                            "message" :{
                                "type" : "string"
                            }
                        },
                        "required" :["answered","message"]
                    }
                }
            )
            ai_response : dict = json.loads(response.text)
            return{
                "answered" : ai_response["answered"],
                "message" : ai_response["message"]
            }
        except geniai_errors.ServerError:
            if attempt == max_tries -1:
                return {
                    "answered" : False,
                    "message" : "I'm sorry, our AI service is temporarily unavailable. Please try again in a moment."
                }
            await asyncio.sleep(2 ** attempt)
        except geniai_errors.ClientError:
            return{
                "answered" : False,
                "message" : "I'm sorry, I'm unable to process your request right now. Please try again later."
            }

        except (KeyError, json.JSONDecodeError):
            if attempt == max_tries -1:
                return{
                    "answered" : False,
                    "message" : "I'm sorry, I couldn't find that information. Please contact the hotel reception for further assistance."
                }
             
