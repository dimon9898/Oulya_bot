from app.bot_init import bot
from app.database.repository.requests import update_payment_status
from sqlalchemy.ext.asyncio import AsyncSession

async def payment_notify(session: AsyncSession, payload: dict):
    if payload.get('event') == 'payment.succeeded':
        metadata = payload.get('object', {}).get('metadata', {})

        payment_id = payload.get('object', {}).get('id')
        user_id = int(metadata.get('user_id'))
        payment_status = payload.get('event')

        success = await update_payment_status(session, payment_id, payment_status)
        if success:
            await bot.send_message(chat_id=user_id, text='Платеж успешно выполнен!')
        else:
            await bot.send_message(chat_id=user_id, text='Ошибка при обновление платежа!')
