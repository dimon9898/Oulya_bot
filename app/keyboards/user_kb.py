from app.keyboards.keyboard_init import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton
from maxapi.enums.intent import Intent

from config import settings
import app.database.repository.requests as rq

async def user_start_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='🚀 Старт', payload='user_start', intent=Intent.NEGATIVE))
    return kb.adjust(1).as_markup()


async def user_main_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='🎨 Что в канале ?', payload='whats_in_the_chanel', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='🎁 Бесплатный урок', payload='client_free_lesson', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='💎 Платные курсы', payload='client_paid_courses', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='📚 Мои курсы', payload='client_my_purchases', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='🛍 Где купить материалы', payload='client_shop', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='📱 Соц сети', payload='client_social_site', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='✉️ Написать нам', payload='client_feedback', intent=Intent.POSITIVE))
    kb.add(LinkButton(text='📢 Перейти в канал', url=settings.CHANEL_LINK, intent=Intent.DEFAULT))

    return kb.adjust(2, 2, 1, 2, 1).as_markup()


async def what_is_chanel_kb():
    kb = InlineKeyboardBuilder()
    kb.add(LinkButton(text='Перейти в канал', url=settings.CHANEL_LINK))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))
    return kb.adjust(1).as_markup()


async def client_free_sign_subscription_kb(session, member):
    kb = InlineKeyboardBuilder()
    if member is None:
        kb.add(LinkButton(text='📢 Подписаться на канал', url=settings.CHANEL_LINK))
        kb.add(CallbackButton(text='✅ Я подписался', payload='client_free_check_subscription'))
    else:
        free_course = await rq.get_free_course(session)
        kb.add(CallbackButton(text=f'{free_course.title}', payload=f'free_course_{free_course.id}'))

    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))

    return kb.adjust(1).as_markup()   

async def client_courses_sign_subscription_kb():
    kb = InlineKeyboardBuilder()
    kb.add(LinkButton(text='📢 Подписаться на канал', url=settings.CHANEL_LINK))
    kb.add(CallbackButton(text='✅ Я подписался', payload='client_courses_check_subscription'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))

    return kb.adjust(2, 1).as_markup()

async def client_courses_list_kb(courses):
    kb = InlineKeyboardBuilder()
    if courses:
        for c in courses:
            kb.add(CallbackButton(text=c.title, payload=f'client_course_{c.id}'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))
    return kb.adjust(1).as_markup()

async def course_buy_kb(course_id):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='Купить', payload=f'click_buy_course_{course_id}'))
    kb.add(CallbackButton(text='⬅ назад', payload='client_paid_courses'))
    return kb.adjust(1).as_markup()


async def free_course_kb():
    pass


async def shop_kbs():
    kb = InlineKeyboardBuilder()
    kb.add(LinkButton(text='🛍️ Wildberries', url='https://www.wildberries.ru/brands/312172703-hobbi-uley'))
    kb.add(LinkButton(text='🛍️ Ozon', url='https://ozon.ru/t/6joEdZL'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))
    return kb.adjust(2, 1).as_markup()


async def social_kbs():
    kb = InlineKeyboardBuilder()
    kb.add(LinkButton(text='📺 VK', url='https://vk.ru/hobbylei'))
    kb.add(LinkButton(text='🎞️ Youtube', url='https://youtube.com/@hobbyylei?si=OgKilq_pAQfogThv'))
    kb.add(LinkButton(text='📱 Instagram', url='https://www.instagram.com/hobbyylei/'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))
    return kb.adjust(2, 1, 1).as_markup()


async def my_courses_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='Мои курсы', payload='client_my_purchases'))
    kb.add(CallbackButton(text='⬅ Главное меню', payload='back_to_user_main'))
    return kb.adjust(1).as_markup()


async def purchased_courses_kb(purchases):
    kb = InlineKeyboardBuilder()
    if purchases:
        for p in purchases:
            kb.add(CallbackButton(text=p.course.title, payload=f'purchased_{p.course_id}'))
    kb.add(CallbackButton(text='назад', payload='back_to_user_main')) 
    return kb.adjust(1).as_markup()     