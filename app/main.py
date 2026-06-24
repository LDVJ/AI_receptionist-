from fastapi import FastAPI
from .routes import login, hotel, user, faqs

app =  FastAPI()


@app.get("/")
def root():
    return {
        "message":"FastAPI running"
    }


app.include_router(user.router)
app.include_router(login.router)
app.include_router(hotel.router)
app.include_router(faqs.router)