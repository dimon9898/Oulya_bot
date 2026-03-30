from maxapi import Bot, Dispatcher
from config import settings
from maxapi.types.command import BotCommand

bot = Bot(token=settings.MAX_TOKEN)
dp = Dispatcher()


async def bot_set_commands():
    commands = [
        BotCommand(name='start', description='🔄 Перезапуск бота'),
        BotCommand(name='main', description='🏠 Главное меню'),
        BotCommand(name='help', description='📮 Чат с админом')
    ]


    await bot.set_my_commands(commands)