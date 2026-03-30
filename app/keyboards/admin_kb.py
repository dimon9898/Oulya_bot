from app.keyboards.keyboard_init import InlineKeyboardBuilder
from maxapi.types import CallbackButton

async def admin_panel_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='Конкурс', payload='admin_confest'))
    return kb.adjust(1).as_markup()