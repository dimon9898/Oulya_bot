import asyncio
from maxapi.enums.parse_mode import ParseMode
from app.bot_init import bot
from app.database.repository.requests import update_payment_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.user_kb import my_courses_kb

async def payment_notify(session: AsyncSession, payload: dict):
    if payload.get('event') == 'payment.succeeded':
        metadata = payload.get('object', {}).get('metadata', {})

        payment_id = payload.get('object', {}).get('id')
        user_id = int(metadata.get('user_id'))
        payment_status = payload.get('event')

        success = await update_payment_status(session, payment_id, payment_status)
        if success:
            await asyncio.sleep(3)
            await bot.send_message(user_id=user_id, text='<b>Платеж успешно выполнен!</b>\n\n'
                                   f'<b>Номер платежа:</b> <code>{payment_id}</code>',
                                                        parse_mode=ParseMode.HTML
                                                        )
            await asyncio.sleep(2)
            await bot.send_message(user_id=user_id, text='Ваш курс ждет вас в <b>"Мои курсы"</b>',
                                                        attachments=[
                                                            await my_courses_kb(),
                                                        ], parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(user_id=user_id, text='Ошибка при обновление платежа!')
