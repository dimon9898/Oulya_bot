from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback, Command

from config import settings



admin = Router()


@admin.message_created(Command('admin'), lambda event: event.message.sender.user_id in settings.ADMIN_IDS)
async def cmd_admin(event: MessageCreated):
    await event.message.answer('Доступ к админ-панель разрещен!')
    