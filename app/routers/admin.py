from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback, Command

from config import settings



admin = Router()

@admin.message_created(F.from_user.user_id.in_(settings.ADMIN_IDS))
async def cmd_admin(event: MessageCreated):
    await event.message.answer('Доступ к админ-панели разрешён!')