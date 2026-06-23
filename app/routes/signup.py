from fastapi import APIRouter


router = APIRouter(
    tags=["Signup"],
)

@router.post("/signup")
async def signup():
    return  {
        "message" : "Signup URL Reached"
    }