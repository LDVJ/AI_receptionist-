from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import login, hotel, user, faqs,chat

app =  FastAPI()


@app.get("/")
def root():
    return {
        "message":"FastAPI running"
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://127.0.0.1:5500"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


app.include_router(user.router)
app.include_router(login.router)
app.include_router(hotel.router)
app.include_router(faqs.router)
app.include_router(chat.router)