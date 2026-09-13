import asyncio
import csv
import io
from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.types.attachments.upload import AttachmentPayload, AttachmentUpload
from maxapi.enums.upload_type import UploadType
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode
from maxapi.filters.filter import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

import app.keyboards.admin_kb as kb
import app.database.repository.admin_reqs as rq
import app.database.repository.contest_reqs as crq

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
    await event.message.delete()
    await event.message.answer('Доступ к админ-панели разрешён!', 
                                attachments=[await kb.admin_panel_kb()])

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



@admin.message_callback(F.callback.payload == 'admin_statistics', IsAdmin())
async def admin_statistics(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    result = await rq.get_statistics_bot(session)
    count = result['count']
    total = result['total_sum']
    new_users = result['new_users']
    payment_count = result['payment_count']
    sources = result['sources']
    
    statistics_text = (
        '📊 <b>Статистика</b>\n\n'
        f'👥 Количество пользователей: <b>{count}</b>\n'
        '----------------------------------------------\n'
        f'🆕 Новых за 7 дней: +<b>{new_users}</b>\n'
        '----------------------------------------------\n'
        f'💰 Выручка от продажи курсов: <b>{total}</b> руб.\n'
        '----------------------------------------------\n'
        f'🧮 Количество платежей: <b>{payment_count}</b>\n'
        '----------------------------------------------\n\n'
        f'📈 Статистика переходов по ссылкам:\n\n'
    )

    platform = {
        'direct': 'Max',
        'Wildberries': 'Wildberries',
        'Ozon': 'Ozon',
        'Youtube': 'Youtube',
        'Tiktok': 'TikTok'
    }

    for source, label in platform.items():
        count = sources.get(source, 0)
        statistics_text += f'🔶 -> {label}: {count}\n'
        statistics_text += '----------------------------------------------\n'

    
    await event.message.answer(statistics_text, parse_mode=ParseMode.HTML,
                               attachments=[
                                   await kb.update_statistics_btn()
                               ])      
    

@admin.message_callback(F.callback.payload == 'admin_update_statistics')
async def admin_update_statistics(event: MessageCallback, session: AsyncSession):
    await admin_statistics(event, session)


# ---------- Модерация конкурса ----------

def _work_admin_caption(work) -> str:
    category = crq.CATEGORY_LABELS.get(work.category, work.category)
    status = crq.STATUS_LABELS.get(work.status, work.status)
    return (
        f'<b>Работа №{work.number:03d}</b>\n'
        f'Автор: {work.author_name}, {work.author_age} лет ({category})\n'
        f'Username: {work.author_username or "—"}\n'
        f'Название: «{work.title}»\n'
        f'Описание: {work.description or "—"}\n'
        f'Статус: <b>{status}</b>'
    )


async def _send_work_card(event, work, page: int, total_pages: int):
    await event.message.answer(
        text=_work_admin_caption(work),
        attachments=[
            AttachmentUpload(
                type=UploadType.IMAGE,
                payload=AttachmentPayload(token=work.final_photo),
            ),
            AttachmentUpload(
                type=UploadType.IMAGE,
                payload=AttachmentPayload(token=work.process_photo),
            ),
            await kb.contest_moderation_kb(work.id, page, total_pages),
        ],
        parse_mode=ParseMode.HTML,
    )


@admin.message_callback(F.callback.payload == 'admin_contest_manage')
async def admin_contest_manage(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await event.message.answer('Конкурс не настроен.')
        return
    await event.message.answer(
        text=f'<b>🏆 Управление конкурсом</b>\n\n{contest_obj.title or ""}',
        attachments=[await kb.contest_admin_kb(contest_obj.voting_open)],
        parse_mode=ParseMode.HTML,
    )


@admin.message_callback(F.callback.payload.startswith('admin_contest_pending'))
async def admin_contest_pending(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    await _show_moderation_page(event, session, 'pending', 0)


@admin.message_callback(F.callback.payload.startswith('admin_contest_approved'))
async def admin_contest_approved(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    await _show_moderation_page(event, session, 'approved', 0)


@admin.message_callback(F.callback.payload.startswith('admin_contest_rejected'))
async def admin_contest_rejected(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    await _show_moderation_page(event, session, 'rejected', 0)


@admin.message_callback(F.callback.payload.startswith('admin_contest_page_'))
async def admin_contest_page(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    page = int(event.callback.payload.split('_')[-1])
    await _show_moderation_page(event, session, 'pending', page)


async def _show_moderation_page(event, session: AsyncSession, status: str, page: int):
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await event.message.answer('Конкурс не настроен.')
        return

    total = await crq.count_works(session, contest_obj.id, status)
    if total == 0:
        await event.message.answer(
            f'Нет работ со статусом «{crq.STATUS_LABELS.get(status, status)}».',
            attachments=[await kb.contest_admin_kb(contest_obj.voting_open)],
        )
        return

    page_size = settings.CONTEST_PAGE_SIZE
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))

    works = await crq.get_works_by_status(
        session, contest_obj.id, status, offset=page * page_size, limit=page_size
    )

    await event.message.answer(
        text=f'<b>{crq.STATUS_LABELS.get(status, status)}</b> — стр. {page + 1}/{total_pages} (всего {total})',
        parse_mode=ParseMode.HTML,
    )
    for work in works:
        await asyncio.sleep(1)
        await _send_work_card(event, work, page, total_pages)


@admin.message_callback(F.callback.payload.startswith('admin_work_approve_'))
async def admin_work_approve(event: MessageCallback, session: AsyncSession):
    work_id = int(event.callback.payload.split('_')[-1])
    await crq.update_work_status(session, work_id, 'approved')
    await event.message.answer('✅ Работа допущена.')


@admin.message_callback(F.callback.payload.startswith('admin_work_reject_'))
async def admin_work_reject(event: MessageCallback, session: AsyncSession):
    work_id = int(event.callback.payload.split('_')[-1])
    await crq.update_work_status(session, work_id, 'rejected')
    await event.message.answer('❌ Работа отклонена.')


@admin.message_callback(F.callback.payload.startswith('admin_work_proof_'))
async def admin_work_proof(event: MessageCallback, session: AsyncSession):
    work_id = int(event.callback.payload.split('_')[-1])
    work = await crq.update_work_status(session, work_id, 'need_proof')
    if not work:
        await event.message.answer('Работа не найдена.')
        return
    await event.message.answer('❓ Запрошено подтверждение авторства.')
    try:
        await event.bot.send_message(
            chat_id=work.user_id,
            text=(
                'Нам нужно немного больше информации для проверки авторства.\n'
                'Пожалуйста, пришлите фото работы с другого ракурса или короткое видео.'
            ),
        )
    except Exception:
        pass


@admin.message_callback(F.callback.payload == 'admin_contest_vote_open')
async def admin_contest_vote_open(event: MessageCallback, session: AsyncSession):
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        return
    await crq.set_voting_open(session, contest_obj.id, True)
    await event.message.delete()
    await event.message.answer('🗳 Голосование открыто.',
                               attachments=[await kb.contest_admin_kb(True)])


@admin.message_callback(F.callback.payload == 'admin_contest_vote_close')
async def admin_contest_vote_close(event: MessageCallback, session: AsyncSession):
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        return
    await crq.set_voting_open(session, contest_obj.id, False)
    await event.message.delete()
    await event.message.answer('🔒 Голосование закрыто.',
                               attachments=[await kb.contest_admin_kb(False)])


@admin.message_callback(F.callback.payload == 'admin_contest_results')
async def admin_contest_results(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        return

    results = await crq.get_results(session, contest_obj.id)
    if not results['all']:
        await event.message.answer('Пока нет результатов.',
                                   attachments=[await kb.contest_results_kb()])
        return

    text = '<b>📊 Результаты конкурса</b>\n\n'
    for category, label in crq.CATEGORY_LABELS.items():
        text += f'<b>🏆 {label}</b>\n'
        cat_rows = results['by_category'].get(category, [])
        if not cat_rows:
            text += '— нет работ\n\n'
            continue
        for work, votes in cat_rows[:3]:
            text += f'№{work.number:03d} «{work.title}» — {votes} голосов\n'
        text += '\n'

    await event.message.answer(text=text, attachments=[await kb.contest_results_kb()],
                               parse_mode=ParseMode.HTML)


@admin.message_callback(F.callback.payload == 'admin_contest_export')
async def admin_contest_export(event: MessageCallback, session: AsyncSession):
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        return

    results = await crq.get_results(session, contest_obj.id)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Номер', 'Название', 'Автор', 'Возраст', 'Категория', 'Статус', 'Голосов'])
    for work, votes in results['all']:
        writer.writerow([
            work.number,
            work.title,
            work.author_name,
            work.author_age,
            crq.CATEGORY_LABELS.get(work.category, work.category),
            crq.STATUS_LABELS.get(work.status, work.status),
            votes,
        ])

    csv_bytes = buffer.getvalue().encode('utf-8-sig')
    await event.message.answer(
        text='📤 Выгрузка результатов:',
        attachments=[
            AttachmentUpload(
                type=UploadType.FILE,
                payload=AttachmentPayload(
                    token=None,
                    filename=f'contest_{contest_obj.id}_results.csv',
                    data=csv_bytes,
                ),
            )
        ],
    )
