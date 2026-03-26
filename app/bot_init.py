from maxapi import Bot, Dispatcher
from config import settings

bot = Bot(token=settings.MAX_TOKEN)
dp = Dispatcher()