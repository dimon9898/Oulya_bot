from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import webhooks
from app.bot_init import bot, dp
from app.database.db_init import DbSessionMiddleware, async_session
from app.routers.user import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключаем роутеры и middleware
    dp.include_routers(user)
    dp.middleware(DbSessionMiddleware(async_session))
    # Инициализируем диспетчер
    await dp._Dispatcher__ready(bot)
    yield
    # Завершение
    await bot.session.close()



app = FastAPI(lifespan=lifespan)

app.include_router(webhooks.router)


@app.get('/')
async def solo():
    return {'message': 'FastAPI ready!'}