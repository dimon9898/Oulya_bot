import logging

from maxapi import Bot, Dispatcher
from config import settings
from maxapi.types.command import BotCommand

logger = logging.getLogger(__name__)

bot = Bot(token=settings.MAX_TOKEN)
dp = Dispatcher()


async def bot_set_commands():
    commands = [
        BotCommand(name='start', description='🔄 Перезапуск бота'),
        BotCommand(name='main', description='🏠 Главное меню'),
        BotCommand(name='help', description='📮 Чат с админом')
    ]

    try:
        await bot.set_commands(*commands)
    except Exception:
        logger.exception('Не удалось зарегистрировать команды бота, продолжаем без них')
