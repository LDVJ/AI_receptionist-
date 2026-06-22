from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


DB_URL = f'postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

engine = create_async_engine(DB_URL, echo = True)

sessionLocal = async_sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

print(DB_URL)

async def get_db():
    async with sessionLocal() as db:
        print("=====db Connected")
        yield db