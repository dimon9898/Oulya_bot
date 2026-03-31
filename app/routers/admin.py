from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback, Command

from config import settings



admin = Router()

@admin.message_created(Command('admin'))
async def cmd_admin(event: MessageCreated):
    if event.from_user.user_id in settings.ADMIN_IDS:
        await event.message.answer('Доступ к админ-панели разрешён!')