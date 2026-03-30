from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import webhooks
from app.bot_init import bot, dp
from app.bot_init import bot_set_commands
from app.database.db_init import DbSessionMiddleware, async_session
from app.routers.user import user
from app.routers.admin import admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot_set_commands()
    dp.include_routers(user, admin)
    dp.middleware(DbSessionMiddleware(async_session))
    await dp._Dispatcher__ready(bot)

    yield

    await bot.session.close()



app = FastAPI(lifespan=lifespan)

app.include_router(webhooks.router)


@app.get('/')
async def solo():
    return {'message': 'FastAPI ready!'}