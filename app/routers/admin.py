import asyncio
import csv
import io
import logging
from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback, InputMediaBuffer
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


logger = logging.getLogger(__name__)


class Form(StatesGroup):
    title = State()
    description = State()


class IsAdmin(BaseFilter):
    async def __call__(self, event: MessageCreated | MessageCallback) -> bool:
        if event.from_user is None:
            return False
        
        return event.from_user.user_id in settings.ADMIN_IDS


admin = Router()

@admin.message_created(Command('admin'), IsAdmin())
async def cmd_admin(event: MessageCreated):
    await event.message.answer('Доступ к админ-панели разрешён!', 
                                attachments=[await kb.admin_panel_kb()])



@admin.message_callback(F.callback.payload == 'back_to_admin_main', IsAdmin())
async def back_to_admin_main(event: MessageCallback):
    await event.message.delete()
    await event.message.answer('Доступ к админ-панели разрешён!', 
                                attachments=[await kb.admin_panel_kb()])


@admin.message_callback(F.callback.payload.startswith('contest_'), IsAdmin())
async def contest_state(event: MessageCallback, session: AsyncSession):
    parts = event.callback.payload.split('_')
    action = parts[1]

    if len(parts) > 2 and parts[2].isdigit():
        contest_id = int(parts[2])
    else:
        current = await rq.get_contest_status(session)
        if not current:
            await event.message.delete()
            await event.message.answer('Конкурс ещё не настроен.')
            return
        contest_id = current.id

    await event.message.delete()

    contest = await rq.update_contest_state(session, action, contest_id)
    if not contest:
        await event.message.answer('Конкурс не найден.')
        return

    if contest.enabled:
        await event.message.answer(f'Конкурс "{contest.description}" включен ✅', 
                                   attachments=[await kb.contest_kb(contest.enabled)])
    else:
        await event.message.answer(f'Конкурс "{contest.description}" отключен ❌',
                                   attachments=[await kb.contest_kb(contest.enabled)])



@admin.message_callback(F.callback.payload.startswith('admin_contest_edit_title_'), IsAdmin())
async def edit_contest_title_prompt(event: MessageCallback, session: AsyncSession, context: MemoryContext):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[4])
    await event.message.answer('Введите название конкурса: ')
    await context.update_data(contest_id=contest_id, is_new=False)
    await context.set_state(Form.title)




@admin.message_created(Form.title, F.message.body.text, IsAdmin())
async def save_contest_title(event: MessageCreated, session: AsyncSession, context: MemoryContext):
    await context.update_data(title=event.message.body.text)
    data = await context.get_data()
    title = data.get('title', '')
    is_new = bool(data.get('is_new', False))

    if is_new:
        contest = await rq.create_contest(session, title)
        if not contest:
            await event.message.answer('Ошибка при создании конкурса!')
            await context.clear()
            return
        result = rq.UpdateContest(contest=contest, is_updated=True)
    else:
        contest_id = int(data.get('contest_id', ''))
        result = await rq.update_contest_title(session, contest_id, title)

    if result.is_updated:
        if is_new:
            await event.message.answer('Конкурс создан! ✅')
        else:
            await event.message.answer('Название конкурса обновлено! ✅')
        await asyncio.sleep(1)
        await event.message.answer('Панель конкурса', 
                                   attachments=[ 
                                       await kb.contest_admin_kb(result.contest.voting_open, result.contest.id, result.contest.results_published)
                                    ])
    else:
        await event.message.answer('Ошибка при обновление название конкурса!')

    await context.clear()        



@admin.message_callback(F.callback.payload.startswith('admin_contest_edit_description_'), IsAdmin())
async def edit_contest_description_prompt(event: MessageCallback, session: AsyncSession, context: MemoryContext):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[4])
    await event.message.answer('Введите описание конкурса: ')
    await context.update_data(contest_id=contest_id)
    await context.set_state(Form.description)




@admin.message_created(Form.description, F.message.body.text, IsAdmin())
async def save_contest_description(event: MessageCreated, session: AsyncSession, context: MemoryContext):
    await context.update_data(description=event.message.body.text)
    data = await context.get_data()
    contest_id = int(data.get('contest_id', ''))
    description = data.get('description', '')
    result = await rq.update_contest_description(session, contest_id, description)
    if result.is_updated:
        await event.message.answer('Описание конкурса обновлено! ✅')
        await asyncio.sleep(1)
        await event.message.answer('Панель конкурса', attachments=[
            await kb.contest_admin_kb(result.contest.voting_open, result.contest.id, result.contest.results_published)
        ])
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
    

@admin.message_callback(F.callback.payload == 'admin_update_statistics', IsAdmin())
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


async def _send_work_card(event, work, page: int, total_pages: int, status: str, contest_id: int):
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
            await kb.contest_moderation_kb(work.id, page, total_pages, status, contest_id),
        ],
        parse_mode=ParseMode.HTML,
    )


@admin.message_callback(F.callback.payload == 'admin_contest_manage', IsAdmin())
async def admin_contest_manage(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contests = await crq.get_all_contests(session)
    await event.message.answer('Выберите конкурс:', attachments=[await kb.admin_contests_kb(contests)])


@admin.message_callback(F.callback.payload == 'admin_add_contest', IsAdmin())
async def admin_add_contest(event: MessageCallback, context: MemoryContext):
    await event.message.delete()
    await event.message.answer('Введите название конкурса: ')
    await context.update_data(is_new=True)
    await context.set_state(Form.title)


@admin.message_callback(F.callback.payload.startswith('admin_select_contest_'), IsAdmin())
async def admin_select_contest(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[3])
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        await event.message.answer('Конкурс не настроен.')
        return
    await event.message.answer(
        text=f'<b>🏆 Управление конкурсом</b>\n\n{contest_obj.title or ""}',
        attachments=[await kb.contest_admin_kb(contest_obj.voting_open, contest_obj.id, contest_obj.results_published)],
        parse_mode=ParseMode.HTML,
    )


@admin.message_callback(F.callback.payload.startswith('admin_contest_delete_'), IsAdmin())
async def admin_contest_delete(event: MessageCallback, session: AsyncSession):
    contest_id = int(event.callback.payload.split('_')[3])
    contest_obj = await rq.update_contest_state(session, 'off', contest_id)
    if not contest_obj:
        await event.message.answer('Конкурс не найден.')
        return

    await event.message.delete()
    contests = await crq.get_all_contests(session)
    active = [c for c in contests if c.enabled]
    if not active:
        await event.message.answer('Конкурс удалён ✅\n\nНет активных конкурсов.')
        return

    await event.message.answer(
        'Конкурс удалён ✅\n\nВыберите конкурс:',
        attachments=[await kb.admin_contests_kb(contests)],
    )


@admin.message_callback(F.callback.payload.startswith('admin_contest_pending_'), IsAdmin())
async def admin_contest_pending(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[3])
    await _show_moderation_page(event, session, 'pending', 0, contest_id)


@admin.message_callback(F.callback.payload.startswith('admin_contest_approved_'), IsAdmin())
async def admin_contest_approved(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[3])
    await _show_moderation_page(event, session, 'approved', 0, contest_id)


@admin.message_callback(F.callback.payload.startswith('admin_contest_rejected_'), IsAdmin())
async def admin_contest_rejected(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[3])
    await _show_moderation_page(event, session, 'rejected', 0, contest_id)


@admin.message_callback(F.callback.payload.startswith('admin_contest_page_'), IsAdmin())
async def admin_contest_page(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    parts = event.callback.payload.split('_')
    status = parts[3]
    contest_id = int(parts[4])
    page = int(parts[5])
    await _show_moderation_page(event, session, status, page, contest_id)


async def _show_moderation_page(event, session: AsyncSession, status: str, page: int, contest_id: int):
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        await event.message.answer('Конкурс не настроен.')
        return

    total = await crq.count_works(session, contest_obj.id, status)
    if total == 0:
        await event.message.answer(
            f'Нет работ со статусом «{crq.STATUS_LABELS.get(status, status)}».',
            attachments=[await kb.contest_admin_kb(contest_obj.voting_open, contest_obj.id, contest_obj.results_published)],
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
        await _send_work_card(event, work, page, total_pages, status, contest_obj.id)


@admin.message_callback(F.callback.payload.startswith('admin_work_approve_'), IsAdmin())
async def admin_work_approve(event: MessageCallback, session: AsyncSession):
    work_id = int(event.callback.payload.split('_')[-1])
    work = await crq.update_work_status(session, work_id, 'approved')
    await event.message.edit(text='✅ Работа допущена.', attachments=[await kb.back_to_admin_contest_manage()])
    if work:
        try:
            await event.bot.send_message(
                chat_id=work.user_id,
                text=(
                    f'🎉 Ваша работа №{work.number:03d} «{work.title}» допущена к конкурсу!\n'
                    'Теперь её можно увидеть в разделе «Все работы», и за неё можно голосовать.'
                ),
            )
        except Exception:
            logger.exception('Не удалось уведомить автора работы %s', work_id)


@admin.message_callback(F.callback.payload.startswith('admin_work_reject_'), IsAdmin())
async def admin_work_reject(event: MessageCallback, session: AsyncSession):
    work_id = int(event.callback.payload.split('_')[-1])
    work = await crq.update_work_status(session, work_id, 'rejected')
    await event.message.edit(text='❌ Работа отклонена.', attachments=[await kb.back_to_admin_contest_manage()])
    if work:
        try:
            await event.bot.send_message(
                chat_id=work.user_id,
                text=(
                    f'😔 К сожалению, ваша работа №{work.number:03d} «{work.title}» отклонена модератором.\n'
                    'Вы можете отправить новую работу, пока приём заявок открыт.'
                ),
            )
        except Exception:
            logger.exception('Не удалось уведомить автора работы %s', work_id)


@admin.message_callback(F.callback.payload.startswith('admin_work_proof_'), IsAdmin())
async def admin_work_proof(event: MessageCallback, session: AsyncSession):
    work_id = int(event.callback.payload.split('_')[-1])
    work = await crq.update_work_status(session, work_id, 'need_proof')
    if not work:
        await event.message.answer('Работа не найдена.', attachments=[await kb.back_to_admin_contest_manage()])
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


@admin.message_callback(F.callback.payload.startswith('admin_contest_vote_open_'), IsAdmin())
async def admin_contest_vote_open(event: MessageCallback, session: AsyncSession):
    contest_id = int(event.callback.payload.split('_')[4])
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        return
    await crq.set_voting_open(session, contest_obj.id, True)
    await event.message.delete()
    await event.message.answer('🗳 Голосование открыто.',
                               attachments=[await kb.contest_admin_kb(True, contest_obj.id, contest_obj.results_published)])


@admin.message_callback(F.callback.payload.startswith('admin_contest_vote_close_'), IsAdmin())
async def admin_contest_vote_close(event: MessageCallback, session: AsyncSession):
    contest_id = int(event.callback.payload.split('_')[4])
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        return
    await crq.set_voting_open(session, contest_obj.id, False)
    await event.message.delete()
    await event.message.answer('🔒 Голосование закрыто.',
                               attachments=[await kb.contest_admin_kb(False, contest_obj.id, contest_obj.results_published)])


async def _notify_participants_results(event, session: AsyncSession, contest_obj):
    """Отправляет персональные уведомления участникам конкурса
    об опубликованных результатах."""
    results = await crq.get_results(session, contest_obj.id)

    place_map: dict[int, int] = {}
    for _category, rows in results.get('by_category', {}).items():
        for idx, (work, _votes) in enumerate(rows, start=1):
            place_map[work.id] = idx

    # на каждого участника — одно сообщение по его лучшей работе
    best_by_user: dict[int, tuple] = {}
    for work, votes in results.get('all', []):
        current = best_by_user.get(work.user_id)
        if current is None or votes > current[1]:
            best_by_user[work.user_id] = (work, votes)

    medals = {1: '🥇', 2: '🥈', 3: '🥉'}
    title = contest_obj.title or 'Конкурс'

    for user_id, (work, votes) in best_by_user.items():
        place = place_map.get(work.id)
        if place in medals:
            place_line = f'{medals[place]} {place} место'
        elif place:
            place_line = f'{place} место'
        else:
            place_line = f'{votes} голосов'

        text = (
            f'🏅 Результаты конкурса «{title}» опубликованы!\n\n'
            f'Ваша работа №{work.number:03d} «{work.title}» набрала {votes} голосов '
            f'и заняла {place_line} в своей категории.\n\n'
            'Спасибо за участие! 💛'
        )
        try:
            await event.bot.send_message(chat_id=user_id, text=text)
        except Exception:
            logger.exception('Не удалось уведомить участника %s конкурса %s', user_id, contest_obj.id)


@admin.message_callback(F.callback.payload.startswith('admin_contest_publish_'), IsAdmin())
async def admin_contest_publish(event: MessageCallback, session: AsyncSession):
    contest_id = int(event.callback.payload.split('_')[3])
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        await event.message.answer('Конкурс не найден.')
        return

    was_published = contest_obj.results_published
    await crq.set_results_published(session, contest_obj.id, True)
    await event.message.delete()
    await event.message.answer('📢 Результаты опубликованы — участники увидят их в конкурсе.',
                               attachments=[await kb.contest_admin_kb(contest_obj.voting_open, contest_obj.id, True)])

    if not was_published:
        await _notify_participants_results(event, session, contest_obj)


@admin.message_callback(F.callback.payload.startswith('admin_contest_unpublish_'), IsAdmin())
async def admin_contest_unpublish(event: MessageCallback, session: AsyncSession):
    contest_id = int(event.callback.payload.split('_')[3])
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        await event.message.answer('Конкурс не найден.')
        return
    await crq.set_results_published(session, contest_obj.id, False)
    await event.message.delete()
    await event.message.answer('🙈 Результаты скрыты от участников.',
                               attachments=[await kb.contest_admin_kb(contest_obj.voting_open, contest_obj.id, False)])


@admin.message_callback(F.callback.payload.startswith('admin_contest_results'), IsAdmin())
async def admin_contest_results(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[3])
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        return

    results = await crq.get_results(session, contest_obj.id)
    if not results['all']:
        await event.message.answer('Пока нет результатов.',
                                   attachments=[await kb.contest_results_kb(contest_obj.id)])
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

    await event.message.answer(text=text, attachments=[await kb.contest_results_kb(contest_obj.id)],
                               parse_mode=ParseMode.HTML)



CSV_HEADER = ['Номер', 'Название', 'Автор', 'Возраст', 'Категория', 'Статус', 'Голосов']


def build_results_csv(results: list) -> bytes:
    """Собирает CSV в памяти и возвращает байты (UTF-8 с BOM для Excel)."""
    buffer = io.StringIO()
    # ';' лучше открывается в русской локали Excel; если нужна запятая, уберите delimiter
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow(CSV_HEADER)

    for work, votes in results:
        writer.writerow([
            work.number,
            work.title,
            work.author_name,
            work.author_age,
            crq.CATEGORY_LABELS.get(work.category, work.category),
            crq.STATUS_LABELS.get(work.status, work.status),
            votes,
        ])

    return buffer.getvalue().encode('utf-8-sig')


@admin.message_callback(F.callback.payload.startswith('admin_contest_export'), IsAdmin())
async def admin_contest_export(event: MessageCallback, session: AsyncSession):
    # payload вида: admin_contest_export_<contest_id>
    try:
        contest_id = int(event.callback.payload.split('_')[3])
    except (IndexError, ValueError):
        logger.warning('Некорректный payload: %s', event.callback.payload)
        return

    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        await event.message.answer('⚠️ Конкурс не найден или уже неактивен.')
        return

    results = await crq.get_results(session, contest_obj.id)
    all_results = results.get('all', [])

    if not all_results:
        await event.message.answer('ℹ️ В этом конкурсе пока нет работ для выгрузки.')
        return

    csv_bytes = build_results_csv(all_results)

    try:
        await event.message.answer(
            text=f'📤 Выгрузка результатов конкурса «{contest_obj.title or contest_obj.id}»:',
            attachments=[
                InputMediaBuffer(
                    buffer=csv_bytes,
                    type=UploadType.FILE,
                    filename=f'contest_{contest_obj.id}_results.csv',
                )
            ],
        )
    except Exception:
        logger.exception('Не удалось отправить выгрузку конкурса %s', contest_obj.id)
        await event.message.answer('❌ Не удалось отправить файл. Попробуйте позже.')
