from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.filters.command import Command
from maxapi.filters.filter import BaseFilter


from config import settings


class IsAdmin(BaseFilter):
    async def __call__(self, event: MessageCreated) -> bool:
        if event.from_user is None:
            return False
        
        return event.from_user.user_id in settings.ADMIN_IDS


admin = Router()

@admin.message_created(Command('admin'), IsAdmin())
async def cmd_admin(event: MessageCreated):
    await event.message.answer('Доступ к админ-панели разрешён!')