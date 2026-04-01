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