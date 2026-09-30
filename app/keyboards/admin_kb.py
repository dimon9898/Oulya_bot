from app.keyboards.keyboard_init import InlineKeyboardBuilder
from maxapi.types import CallbackButton

from app.database.models import Contest

async def admin_panel_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='🏆 Управление конкурсом', payload='admin_contest_manage'))
    kb.add(CallbackButton(text='Статистика', payload='admin_statistics'))
    return kb.adjust(1).as_markup()


async def admin_contests_kb(contests: list[Contest]):
    kb = InlineKeyboardBuilder()

    active = [c for c in contests if c.enabled]

    for contest in active:
        label = contest.title or contest.description or 'Без названия'
        icon = '✅' if contest.enabled else '❌'
        kb.add(CallbackButton(text=f'{icon} {label} · #{contest.id}', payload=f'admin_select_contest_{contest.id}'))

    kb.add(CallbackButton(text='Добавить ＋', payload='admin_add_contest'))
    kb.add(CallbackButton(text='назад', payload='back_to_admin_main'))
    return kb.adjust(1).as_markup()


async def contest_kb(is_enabled: bool):
    kb = InlineKeyboardBuilder()
    if is_enabled:
        kb.add(CallbackButton(text='Отключить ❌', payload='contest_off'))
    else:
        kb.add(CallbackButton(text='Включить ✅', payload='contest_on'))

    kb.add(CallbackButton(text='назад', payload='back_to_admin_main')) 
    return kb.adjust(1).as_markup()       


async def update_statistics_btn():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='♻️ Обновить', payload='admin_update_statistics'))
    return kb.adjust(1).as_markup()


async def contest_admin_kb(voting_open: bool, contest_id: int, results_published: bool = False):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='📥 Заявки на модерации', payload=f'admin_contest_pending_{contest_id}'))
    kb.add(CallbackButton(text='✅ Допущенные работы', payload=f'admin_contest_approved_{contest_id}'))
    kb.add(CallbackButton(text='❌ Отклонённые работы', payload=f'admin_contest_rejected_{contest_id}'))
    if voting_open:
        kb.add(CallbackButton(text='🔒 Закрыть голосование', payload=f'admin_contest_vote_close_{contest_id}'))
    else:
        kb.add(CallbackButton(text='🗳 Открыть голосование', payload=f'admin_contest_vote_open_{contest_id}'))
    kb.add(CallbackButton(text='📊 Результаты', payload=f'admin_contest_results_{contest_id}'))
    if results_published:
        kb.add(CallbackButton(text='🙈 Скрыть результаты', payload=f'admin_contest_unpublish_{contest_id}'))
    else:
        kb.add(CallbackButton(text='📢 Опубликовать результаты', payload=f'admin_contest_publish_{contest_id}'))
    kb.add(CallbackButton(text='📤 Выгрузить CSV', payload=f'admin_contest_export_{contest_id}'))
    kb.add(CallbackButton(text='✏️ Изменить название', payload=f'admin_contest_edit_title_{contest_id}'))
    kb.add(CallbackButton(text='✏️ Изменить описание', payload=f'admin_contest_edit_description_{contest_id}'))
    kb.add(CallbackButton(text='🗑 Удалить конкурс', payload=f'admin_contest_delete_{contest_id}'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_admin_main'))
    return kb.adjust(1, 1, 1, 1, 1, 1, 1, 2, 1, 1).as_markup()


async def contest_moderation_kb(work_id: int, page: int, total_pages: int, status: str, contest_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='✅ Допустить', payload=f'admin_work_approve_{work_id}'))
    kb.add(CallbackButton(text='❌ Отклонить', payload=f'admin_work_reject_{work_id}'))
    kb.add(CallbackButton(text='❓ Запросить подтверждение', payload=f'admin_work_proof_{work_id}'))
    nav = []
    if page > 0:
        nav.append(CallbackButton(text='⬅', payload=f'admin_contest_page_{status}_{contest_id}_{page - 1}'))
    if page < total_pages - 1:
        nav.append(CallbackButton(text='➡', payload=f'admin_contest_page_{status}_{contest_id}_{page + 1}'))
    if nav:
        kb.add(*nav)
    kb.add(CallbackButton(text='⬅ назад', payload='admin_contest_manage'))
    return kb.adjust(1, 1, 1, len(nav) if nav else 1, 1).as_markup()


async def back_to_admin_contest_manage():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='⬅ назад', payload='admin_contest_manage'))
    return kb.adjust(1).as_markup()



async def contest_results_kb(contest_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='♻️ Обновить', payload=f'admin_contest_results_{contest_id}'))
    kb.add(CallbackButton(text='⬅ назад', payload='admin_contest_manage'))
    return kb.adjust(1).as_markup()



async def admin_contest_pending_list():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='📥 Заявки на модерации', payload='admin_contest_pending'))
    return kb.adjust(1).as_markup()
