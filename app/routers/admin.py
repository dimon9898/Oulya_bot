import asyncio
from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.filters.command import Command
from maxapi.filters.filter import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

import app.keyboards.admin_kb as kb
import app.database.repository.admin_reqs as rq

from config import settings


class Form(StatesGroup):
    description = State()


class IsAdmin(BaseFilter):
    async def __call__(self, event: MessageCreated) -> bool:
        if event.from_user is None:
            return False
        
        return event.from_user.user_id in settings.ADMIN_IDS


admin = Router()

@admin.message_created(Command('admin'), IsAdmin())
async def cmd_admin(event: MessageCreated):
    await event.message.answer('Доступ к админ-панели разрешён!', 
                                attachments=[await kb.admin_panel_kb()])



@admin.message_callback(F.callback.payload == 'back_to_admin_main')
async def back_to_admin_main(event: MessageCallback):
    await cmd_admin(event.message)

@admin.message_callback(F.callback.payload == 'admin_contest')
async def admin_contest(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest = await rq.get_contest_status(session)
    
    if contest.enabled:
        response = 'Кнопка "Конкурс месяца" включена ✅'
    else:
        response = 'Кнопка "Конкурс месяца" отключена ❌'

    await event.message.answer(text=response, attachments=[await kb.contest_kb(contest.enabled)])        


@admin.message_callback(F.callback.payload.startswith('contest_'))
async def contest_state(event: MessageCallback, session: AsyncSession, context: MemoryContext):
    action = event.callback.payload.split('_')[1]
    await event.message.delete()

    if action == 'off':
        contest = await rq.update_contest_state(session, action)
        if contest.enabled == False:
            await event.message.answer('Кнопка "Конкурс месяца" отключена ❌',
                                       attachments=[await kb.contest_kb(contest.enabled)])
    elif action == 'on':
        await event.message.answer('Введите описание конкурса...')
        await context.set_state(Form.description)


@admin.message_created(Form.description, F.message.body.text)
async def update_contest_description(event: MessageCreated, session: AsyncSession, context: MemoryContext):
    await context.update_data(description=event.message.body.text)
    data = await context.get_data()
    description = data.get('description', '')
    success = await rq.update_contest_state(session, description)
    if success:
        await event.message.answer('Описание конкурса обновлено! ✅')
        await asyncio.sleep(1)
        await event.message.answer('Админ-панель', attachments=[await kb.admin_panel_kb()])
    else:
        await event.message.answer('Ошибка при обновление описание конкурса!')

    await context.clear()        