from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback, Command

from config import settings



admin = Router()

admin.filters.append(F.from_user.id.in_(settings.ADMIN_IDS))

@admin.message_created(Command('admin'))
async def cmd_admin(event: MessageCreated):
    await event.message.answer('Доступ к админ-панель разрещен!')
    