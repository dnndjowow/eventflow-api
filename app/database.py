from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']

async_engine = create_async_engine(DATABASE_URL, echo=True)

AsyncLocalHost = async_sessionmaker(async_engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


async def get_async_db():

    async with AsyncLocalHost() as session:
        yield session

