from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import yookassa_webhook
from app.bot_init import bot, dp
from app.database.db_init import DbSessionMiddleware, async_session
from app.routers.user import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    dp.handle_webhook(bot=bot, host='https://oulya.ru/max/webhook')
    dp.include_routers(user)
    dp.middleware(DbSessionMiddleware(async_session))
    
    
    yield

    await bot.session.close()




app = FastAPI(lifespan=lifespan)

app.include_router(yookassa_webhook.router)


@app.get('/')
async def solo():
    return {'message': 'FastAPI ready!'}