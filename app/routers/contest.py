import asyncio
from maxapi import Router, F
from logger_init import logger
from maxapi.types import MessageCreated, MessageCallback
from maxapi.types.attachments.upload import AttachmentPayload, AttachmentUpload
from maxapi.types.attachments.image import AttachmentType, Image
from maxapi.enums.upload_type import UploadType
from maxapi.enums.parse_mode import ParseMode
from maxapi.context import MemoryContext, State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.repository.contest_reqs as crq
import app.keyboards.user_kb as kb
from config import settings


contest = Router()


class SubmitState(StatesGroup):
    author_name = State()
    author_age = State()
    author_username = State()
    title = State()
    description = State()
    final_photo = State()
    process_photo = State()
    confirm = State()


class FindState(StatesGroup):
    number = State()


def _work_caption(work, index: int, total: int) -> str:
    category = crq.CATEGORY_LABELS.get(work.category, work.category)
    return (
        f'<b>Работа №{work.number:03d}</b>\n'
        f'<i>{index} из {total}</i>\n\n'
        f'<b>«{work.title}»</b>\n'
        f'Автор: {work.author_name} ({category})\n\n'
        f'{work.description or ""}'
    )


async def _send_contest_main(event, session: AsyncSession):
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await event.message.answer('Конкурс пока не настроен.')
        return

    submission_open = crq.is_submission_open(contest_obj)
    voting_open = crq.is_voting_open(contest_obj)
    has_finished = await crq.has_finished_vote(session, contest_obj.id, event.from_user.user_id)
    logger.info(
        f'Конкурс: submission_open={submission_open}, voting_open={voting_open}, '
        f'has_finished={has_finished}, enabled={contest_obj.enabled}, '
        f'submission_start={contest_obj.submission_start}, submission_end={contest_obj.submission_end}'
    )

    text = (
        f'<b>🏆 {contest_obj.title or "Конкурс месяца"}</b>\n\n'
        f'{contest_obj.description or ""}'
    )
    await event.message.answer(
        text=text,
        attachments=[await kb.contest_main_kb(submission_open, voting_open, has_finished)],
        parse_mode=ParseMode.HTML,
    )


@contest.message_callback(F.callback.payload == 'client_contest')
async def contest_main(event: MessageCallback, session: AsyncSession, context: MemoryContext):
    logger.info(f'client_contest нажат пользователем {event.from_user.user_id}')
    await context.clear()
    await event.message.delete()
    await _send_contest_main(event, session)


@contest.message_callback(F.callback.payload == 'contest_rules')
async def contest_rules(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    rules = (contest_obj.rules if contest_obj and contest_obj.rules else 'Правила конкурса пока не заданы.')
    await event.message.answer(text=rules, attachments=[await kb.contest_back_kb()])


@contest.message_callback(F.callback.payload == 'contest_all_works')
async def contest_all_works(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    await event.message.answer(
        text='Выберите категорию:',
        attachments=[await kb.contest_categories_kb()],
    )


@contest.message_callback(F.callback.payload.startswith('contest_cat_'))
async def contest_show_category(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await event.message.answer('Конкурс не найден.')
        return

    category = event.callback.payload.replace('contest_cat_', '')
    if category == 'all':
        works = await crq.get_approved_works(session, contest_obj.id)
    else:
        works = await crq.get_approved_works_by_category(session, contest_obj.id, category)

    if not works:
        await event.message.answer('В этой категории пока нет работ.',
                                   attachments=[await kb.contest_back_kb()])
        return

    for work in works:
        caption = (
            f'<b>Работа №{work.number:03d}</b>\n'
            f'<b>«{work.title}»</b>\n'
            f'Автор: {work.author_name} ({crq.CATEGORY_LABELS.get(work.category, work.category)})\n\n'
            f'{work.description or ""}'
        )
        await asyncio.sleep(1)
        await event.message.answer(
            text=caption,
            attachments=[
                AttachmentUpload(
                    type=UploadType.IMAGE,
                    payload=AttachmentPayload(token=work.final_photo),
                )
            ],
            parse_mode=ParseMode.HTML,
        )

    await event.message.answer('Это все работы в выбранной категории.',
                               attachments=[await kb.contest_back_kb()])


@contest.message_callback(F.callback.payload == 'contest_find_work')
async def contest_find_work(event: MessageCallback, context: MemoryContext):
    await event.message.delete()
    await event.message.answer('Введите номер работы (например, 37):',
                               attachments=[await kb.contest_submit_cancel_kb()])
    await context.set_state(FindState.number)


@contest.message_created(FindState.number, F.message.body.text)
async def contest_find_work_result(event: MessageCreated, session: AsyncSession, context: MemoryContext):
    raw = event.message.body.text.strip()
    if not raw.isdigit():
        await event.message.answer('Пожалуйста, введите число.')
        return

    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await context.clear()
        await event.message.answer('Конкурс не найден.')
        return

    work = await crq.get_work_by_number(session, contest_obj.id, int(raw))
    await context.clear()

    if not work or work.status != 'approved':
        await event.message.answer('Работа с таким номером не найдена.',
                                   attachments=[await kb.contest_back_kb()])
        return

    caption = (
        f'<b>Работа №{work.number:03d}</b>\n'
        f'<b>«{work.title}»</b>\n'
        f'Автор: {work.author_name} ({crq.CATEGORY_LABELS.get(work.category, work.category)})\n\n'
        f'{work.description or ""}'
    )
    await event.message.answer(
        text=caption,
        attachments=[
            AttachmentUpload(
                type=UploadType.IMAGE,
                payload=AttachmentPayload(token=work.final_photo),
            ),
            await kb.contest_back_kb(),
        ],
        parse_mode=ParseMode.HTML,
    )


@contest.message_callback(F.callback.payload == 'contest_my_votes')
async def contest_my_votes(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await event.message.answer('Конкурс не найден.')
        return

    works = await crq.get_user_votes(session, contest_obj.id, event.from_user.user_id)
    if not works:
        await event.message.answer('Вы ещё не голосовали.',
                                   attachments=[await kb.contest_back_kb()])
        return

    numbers = ', '.join(f'№{w.number:03d}' for w in works)
    await event.message.answer(
        text=f'<b>📋 Мои голоса</b>\n\nВы выбрали {len(works)} работ:\n{numbers}',
        attachments=[await kb.contest_back_kb()],
        parse_mode=ParseMode.HTML,
    )


# ---------- Подача заявки ----------

@contest.message_callback(F.callback.payload == 'contest_submit')
async def contest_submit_start(event: MessageCallback, session: AsyncSession, context: MemoryContext):
    logger.info(f'contest_submit нажат пользователем {event.from_user.user_id}')
    try:
        await event.message.delete()
    except Exception as exc:
        logger.warning(f'Не удалось удалить сообщение: {exc}')

    await context.clear()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await event.message.answer('Конкурс пока не настроен.',
                                   attachments=[await kb.contest_back_kb()])
        return

    works = contest_obj.works    
    for work in works:
        if work.user_id == event.from_user.user_id:
            if work.status == 'pending':
                await event.message.answer('Ваша работа находится в модерации. Ожидайте...')
                return
            elif work.status == 'approved':
                await event.message.answer('Вы стали участником конкурса!')
                return
            elif work.status == 'rejected':
                await event.message.answer('Ваша предыдущая работа была отклонена модератором. Вы можете отправить новую.')
                break
            
    if not crq.is_submission_open(contest_obj):
        await event.message.answer('Приём работ сейчас закрыт.',
                                   attachments=[await kb.contest_back_kb()])
        return

    await context.clear()
    await event.message.answer('Введите имя автора работы:',
                               attachments=[await kb.contest_submit_cancel_kb()])
    await context.set_state(SubmitState.author_name)


@contest.message_callback(F.callback.payload == 'contest_submit_cancel')
async def contest_submit_cancel(event: MessageCallback, context: MemoryContext):
    await context.clear()
    await event.message.delete()
    await event.message.answer('Подача заявки отменена.',
                               attachments=[await kb.contest_back_kb()])


@contest.message_created(SubmitState.author_name, F.message.body.text)
async def submit_author_name(event: MessageCreated, context: MemoryContext):
    await context.update_data(author_name=event.message.body.text.strip())
    await event.message.answer('Введите возраст автора (число):')
    await context.set_state(SubmitState.author_age)


@contest.message_created(SubmitState.author_age, F.message.body.text)
async def submit_author_age(event: MessageCreated, context: MemoryContext):
    raw = event.message.body.text.strip()
    if not raw.isdigit() or not (1 <= int(raw) <= 120):
        await event.message.answer('Пожалуйста, введите корректный возраст числом.')
        return
    await context.update_data(author_age=int(raw))
    await event.message.answer('Введите ваш username в MAX (или напишите «нет»):')
    await context.set_state(SubmitState.author_username)


@contest.message_created(SubmitState.author_username, F.message.body.text)
async def submit_author_username(event: MessageCreated, context: MemoryContext):
    await context.update_data(author_username=event.message.body.text.strip())
    await event.message.answer('Введите название работы:')
    await context.set_state(SubmitState.title)


@contest.message_created(SubmitState.title, F.message.body.text)
async def submit_title(event: MessageCreated, context: MemoryContext):
    await context.update_data(title=event.message.body.text.strip())
    await event.message.answer('Введите короткое описание работы:')
    await context.set_state(SubmitState.description)


@contest.message_created(SubmitState.description, F.message.body.text)
async def submit_description(event: MessageCreated, context: MemoryContext):
    await context.update_data(description=event.message.body.text.strip())
    await event.message.answer('Пришлите финальное фото работы:')
    await context.set_state(SubmitState.final_photo)


@contest.message_created(SubmitState.final_photo)
async def submit_final_photo(event: MessageCreated, context: MemoryContext):
    attachments = event.message.body.attachments
    if not attachments:
        await event.message.answer('Пожалуйста, пришлите фото.')
        return

    token = None
    for attachment in attachments:
        if isinstance(attachment, Image):
            token = attachment.payload.token
            break

    if not token:
        await event.message.answer('Пожалуйста, пришлите именно изображение.')
        return

    await context.update_data(final_photo=token)
    await event.message.answer('Теперь пришлите фото процесса (недоделанная работа, материалы, руки в процессе):')
    await context.set_state(SubmitState.process_photo)


@contest.message_created(SubmitState.process_photo)
async def submit_process_photo(event: MessageCreated, context: MemoryContext):
    attachments = event.message.body.attachments
    if not attachments:
        await event.message.answer('Пожалуйста, пришлите фото.')
        return

    token = None
    for attachment in attachments:
        if isinstance(attachment, Image):
            token = attachment.payload.token
            break

    if not token:
        await event.message.answer('Пожалуйста, пришлите именно изображение.')
        return

    await context.update_data(process_photo=token)
    await event.message.answer(
        'Подтвердите, что работа выполнена вами или вашим ребёнком:',
        attachments=[await kb.contest_submit_confirm_kb()],
    )
    await context.set_state(SubmitState.confirm)


@contest.message_callback(SubmitState.confirm, F.callback.payload == 'contest_submit_confirm')
async def submit_confirm(event: MessageCallback, session: AsyncSession, context: MemoryContext):
    data = await context.get_data()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        await context.clear()
        await event.message.answer('Конкурс не найден.')
        return

    work = await crq.create_work(
        db=session,
        contest_id=contest_obj.id,
        user_id=event.from_user.user_id,
        author_name=data.get('author_name', ''),
        author_age=int(data.get('author_age', 0)),
        author_username=data.get('author_username', ''),
        title=data.get('title', ''),
        description=data.get('description', ''),
        final_photo=data.get('final_photo', ''),
        process_photo=data.get('process_photo', ''),
    )
    await context.clear()

    if not work:
        await event.message.answer('Не удалось сохранить работу. Попробуйте позже.')
        return

    await event.message.answer(
        text=(
            f'<b>Работа №{work.number:03d} принята на модерацию 💛</b>\n\n'
            'После проверки мы сообщим, допущена ли она к конкурсу.'
        ),
        attachments=[await kb.contest_back_kb()],
        parse_mode=ParseMode.HTML,
    )


# ---------- Голосование ----------

async def _send_vote_card(event, session: AsyncSession, vote_session):
    order = crq.get_session_order(vote_session)
    selected = crq.get_session_selected(vote_session)
    index = vote_session.current_index

    if index >= len(order):
        await _send_vote_summary(event, session, vote_session)
        return

    work = await crq.get_work_by_id(session, order[index])
    if not work:
        vote_session.current_index = index + 1
        await crq.update_vote_session(session, vote_session, current_index=index + 1)
        await _send_vote_card(event, session, vote_session)
        return

    is_selected = work.id in selected
    is_last = index == len(order) - 1
    caption = _work_caption(work, index + 1, len(order))

    await event.message.answer(
        text=caption,
        attachments=[
            AttachmentUpload(
                type=UploadType.IMAGE,
                payload=AttachmentPayload(token=work.final_photo),
            ),
            await kb.contest_work_card_kb(work.id, is_selected, is_last),
        ],
        parse_mode=ParseMode.HTML,
    )


async def _send_vote_summary(event, session: AsyncSession, vote_session):
    selected = crq.get_session_selected(vote_session)
    if len(selected) < settings.CONTEST_MIN_VOTES:
        await event.message.answer(
            text=(
                f'Вы выбрали {len(selected)} работ.\n'
                f'Для отправки голосования нужно выбрать минимум {settings.CONTEST_MIN_VOTES}.'
            ),
            attachments=[await kb.contest_vote_pause_kb()],
        )
        return

    works = []
    for work_id in selected:
        work = await crq.get_work_by_id(session, work_id)
        if work:
            works.append(work)

    numbers = ', '.join(f'№{w.number:03d}' for w in works)
    await event.message.answer(
        text=(
            f'<b>Вы просмотрели все работы.</b>\n'
            f'Вы выбрали {len(works)} работ:\n{numbers}\n\n'
            'Отправить голоса?'
        ),
        attachments=[await kb.contest_vote_confirm_kb()],
        parse_mode=ParseMode.HTML,
    )


@contest.message_callback(F.callback.payload == 'contest_vote_start')
async def contest_vote_start(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    if not crq.is_voting_open(contest_obj):
        await event.message.answer('Голосование сейчас закрыто.',
                                   attachments=[await kb.contest_back_kb()])
        return

    if await crq.has_finished_vote(session, contest_obj.id, event.from_user.user_id):
        await event.message.answer('Вы уже проголосовали. Изменить голоса нельзя.',
                                   attachments=[await kb.contest_back_kb()])
        return

    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session:
        works = await crq.get_approved_works(session, contest_obj.id)
        if not works:
            await event.message.answer('Пока нет допущенных работ.',
                                       attachments=[await kb.contest_back_kb()])
            return
        vote_session = await crq.create_vote_session(
            session, contest_obj.id, event.from_user.user_id, [w.id for w in works]
        )

    await event.message.answer(
        text=(
            'Перед вами все работы конкурса 🎨\n'
            'Они будут показываться в случайном порядке.\n'
            'Отметьте понравившиеся.\n'
            f'Для завершения голосования нужно выбрать минимум {settings.CONTEST_MIN_VOTES} работы.'
        ),
    )
    await _send_vote_card(event, session, vote_session)


@contest.message_callback(F.callback.payload == 'contest_vote_resume')
async def contest_vote_resume(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        return
    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session or vote_session.is_finished:
        await event.message.answer('Сессия голосования не найдена.',
                                   attachments=[await kb.contest_back_kb()])
        return
    await _send_vote_card(event, session, vote_session)


@contest.message_callback(F.callback.payload == 'contest_vote_pause')
async def contest_vote_pause(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    if not contest_obj:
        return
    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session:
        return
    order = crq.get_session_order(vote_session)
    await event.message.answer(
        text=f'Вы просмотрели {vote_session.current_index} из {len(order)} работ.',
        attachments=[await kb.contest_vote_pause_kb()],
    )


@contest.message_callback(F.callback.payload.startswith('contest_select_'))
async def contest_select(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    work_id = int(event.callback.payload.split('_')[-1])
    contest_obj = await crq.get_active_contest(session)
    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session:
        return

    selected = crq.get_session_selected(vote_session)
    if work_id not in selected:
        selected.append(work_id)
    await crq.update_vote_session(session, vote_session, selected=selected)
    await _send_vote_card(event, session, vote_session)


@contest.message_callback(F.callback.payload.startswith('contest_unselect_'))
async def contest_unselect(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    work_id = int(event.callback.payload.split('_')[-1])
    contest_obj = await crq.get_active_contest(session)
    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session:
        return

    selected = crq.get_session_selected(vote_session)
    if work_id in selected:
        selected.remove(work_id)
    await crq.update_vote_session(session, vote_session, selected=selected)
    await _send_vote_card(event, session, vote_session)


@contest.message_callback(F.callback.payload == 'contest_vote_next')
async def contest_vote_next(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session:
        return
    order = crq.get_session_order(vote_session)
    new_index = min(vote_session.current_index + 1, len(order))
    await crq.update_vote_session(session, vote_session, current_index=new_index)
    await _send_vote_card(event, session, vote_session)


@contest.message_callback(F.callback.payload == 'contest_vote_finish')
async def contest_vote_finish(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session:
        return
    await _send_vote_summary(event, session, vote_session)


@contest.message_callback(F.callback.payload == 'contest_vote_submit')
async def contest_vote_submit(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_obj = await crq.get_active_contest(session)
    vote_session = await crq.get_vote_session(session, contest_obj.id, event.from_user.user_id)
    if not vote_session or vote_session.is_finished:
        await event.message.answer('Голосование уже завершено.',
                                   attachments=[await kb.contest_back_kb()])
        return

    selected = crq.get_session_selected(vote_session)
    if len(selected) < settings.CONTEST_MIN_VOTES:
        await event.message.answer(
            f'Нужно выбрать минимум {settings.CONTEST_MIN_VOTES} работы.',
            attachments=[await kb.contest_vote_pause_kb()],
        )
        return

    ok = await crq.save_votes(session, contest_obj.id, event.from_user.user_id, selected)
    if not ok:
        await event.message.answer('Не удалось сохранить голоса. Попробуйте позже.')
        return

    await crq.update_vote_session(session, vote_session, is_finished=True)
    await event.message.answer(
        text='✅ Ваши голоса приняты. Спасибо за участие!',
        attachments=[await kb.contest_back_kb()],
    )


@contest.message_callback(F.callback.payload == 'contest_already_voted')
async def contest_already_voted(event: MessageCallback):
    await event.message.answer('Вы уже проголосовали. Изменить голоса нельзя.',
                               attachments=[await kb.contest_back_kb()])
