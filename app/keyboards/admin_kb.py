from app.keyboards.keyboard_init import InlineKeyboardBuilder
from maxapi.types import CallbackButton

async def admin_panel_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='Конкурс', payload='admin_contest'))
    kb.add(CallbackButton(text='Статистика', payload='admin_statistics'))
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


async def contest_admin_kb(voting_open: bool):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='📥 Заявки на модерации', payload='admin_contest_pending'))
    kb.add(CallbackButton(text='✅ Допущенные работы', payload='admin_contest_approved'))
    kb.add(CallbackButton(text='❌ Отклонённые работы', payload='admin_contest_rejected'))
    if voting_open:
        kb.add(CallbackButton(text='🔒 Закрыть голосование', payload='admin_contest_vote_close'))
    else:
        kb.add(CallbackButton(text='🗳 Открыть голосование', payload='admin_contest_vote_open'))
    kb.add(CallbackButton(text='📊 Результаты', payload='admin_contest_results'))
    kb.add(CallbackButton(text='📤 Выгрузить CSV', payload='admin_contest_export'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_admin_main'))
    return kb.adjust(1).as_markup()


async def contest_moderation_kb(work_id: int, page: int, total_pages: int):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='✅ Допустить', payload=f'admin_work_approve_{work_id}'))
    kb.add(CallbackButton(text='❌ Отклонить', payload=f'admin_work_reject_{work_id}'))
    kb.add(CallbackButton(text='❓ Запросить подтверждение', payload=f'admin_work_proof_{work_id}'))
    nav = []
    if page > 0:
        nav.append(CallbackButton(text='⬅', payload=f'admin_contest_page_{page - 1}'))
    if page < total_pages - 1:
        nav.append(CallbackButton(text='➡', payload=f'admin_contest_page_{page + 1}'))
    if nav:
        kb.add(*nav)
    kb.add(CallbackButton(text='⬅ назад', payload='admin_contest'))
    return kb.adjust(1, 1, 1, len(nav) if nav else 1, 1).as_markup()


async def contest_results_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='♻️ Обновить', payload='admin_contest_results'))
    kb.add(CallbackButton(text='⬅ назад', payload='admin_contest'))
    return kb.adjust(1).as_markup()
