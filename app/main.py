from fastapi import FastAPI
from .routes import signup

app =  FastAPI()


@app.get("/")
def root():
    return {
        "message":"FastAPI running"
    }


app.include_router(signup.router)