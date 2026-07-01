from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from .db import get_db
from sqlalchemy import select
from . import models
from .routes import login, hotel, user, faqs,chat

app =  FastAPI()


@app.get("/")
async def root(db : AsyncSession = Depends(get_db)):
    smt = await db.execute(select(models.Hotel))
    hotel_lsit =  smt.scalars().all()

    return hotel_lsit


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://127.0.0.1:5500",
                     "https://ai-receptionist-frontend-f3eg.onrender.com"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


app.include_router(user.router)
app.include_router(login.router)
app.include_router(hotel.router)
app.include_router(faqs.router)
app.include_router(chat.router)
