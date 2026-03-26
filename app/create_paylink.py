import uuid
from yookassa import Configuration, Payment
from anyio import to_thread

from config import settings

async def create_payment_link(order_id: int, user_id: int, course_id: int, price):
    Configuration.account_id = settings.SHOP_ID
    Configuration.secret_key = settings.SHOP_SECRET_KEY.get_secret_value()
    


    payload = {
        'amount': {
            'value': f'{price:.2f}',
            'currency': 'RUB'
        },

        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://max.ru/id693800725647_bot'
        },

        'capture': True,
        'description': f'Заказ №{order_id}',
        'metadata': {
            'order_id': order_id,
            'user_id': user_id,
            'course_id': course_id
        },

        'receipt': {
            'customer': {
                'email': 'dilshod.khaidkulov@gmail.com',

            },

            'items': [{
                'description': f'Оплата за курса №{course_id}',
                'quantity': 1,
                'amount': {
                    'value': f'{price:.2f}',
                    'currency': 'RUB'
                    },
                'vat_code': 1,
                'payment_mode': 'full_prepayment',
                'payment_subject': 'commodity'    
            }]
        }
    }

    def _generate() -> Payment:
        return Payment.create(payload, uuid.uuid4())
    
    payment: Payment = await to_thread.run_sync(_generate)
    
    confirmation_url = getattr(payment.confirmation, 'confirmation_url', None)
    payment_id = getattr(payment, 'id', None)

    return {'payment_id': payment_id, 'confirmation_url': confirmation_url}
