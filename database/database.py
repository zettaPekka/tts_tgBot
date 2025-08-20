from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

from database.models import Base

import os
from contextlib import asynccontextmanager


load_dotenv()

engine = create_async_engine(os.getenv('DB_PATH'))
session_factory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_db_session():
    async with session_factory() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)