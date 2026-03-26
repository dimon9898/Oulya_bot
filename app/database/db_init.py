from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator

from config import settings

engine = create_async_engine(url=settings.get_db_url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session




class DbSessionMiddleware:
    def __init__(self, session_pool):
        self.session_pool = session_pool

    async def __call__(self, handler, event, data):
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)