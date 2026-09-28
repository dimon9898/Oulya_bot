from app.keyboards.keyboard_init import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton
from maxapi.enums.intent import Intent

from config import settings
from app.database.models import Contest
import app.database.repository.requests as rq

async def user_start_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='🚀 Старт', payload='user_start', intent=Intent.NEGATIVE))
    return kb.adjust(1).as_markup()


async def user_main_kb(enabled: bool):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='🎨 Что в канале ?', payload='whats_in_the_chanel', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='🎁 Бесплатный урок', payload='client_free_lesson', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='💎 Платные курсы', payload='client_paid_courses', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='📚 Мои курсы', payload='client_my_purchases', intent=Intent.POSITIVE))
    if enabled:
        kb.add(CallbackButton(text='🏆 Конкурс месяца(в тестовом режиме)', payload='client_contest'))
    kb.add(CallbackButton(text='🛍 Где купить материалы', payload='client_shop', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='📱 Соц сети', payload='client_social_site', intent=Intent.POSITIVE))
    kb.add(CallbackButton(text='✉️ Написать нам', payload='client_feedback', intent=Intent.POSITIVE))
    kb.add(LinkButton(text='📢 Перейти в канал', url=settings.CHANEL_LINK, intent=Intent.DEFAULT))

    if enabled:
        return kb.adjust(2, 2, 1, 1, 2, 1).as_markup()
    else:
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



async def cancel_buying_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='Отменить', payload='cancel_buying'))
    return kb.adjust(1).as_markup()


async def client_feedback_kb():
    kb = InlineKeyboardBuilder()
    kb.add(LinkButton(text='👉 Написать в личку', url=f'https://max.ru/u/{settings.ADMIN_IDS[0]}'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))
    return kb.adjust(1).as_markup()


async def contest_main_kb(submission_open: bool, voting_open: bool, has_finished_vote: bool, contest_id: int):
    kb = InlineKeyboardBuilder()
    if submission_open:
        kb.add(CallbackButton(text='📝 Участвовать в конкурсе', payload=f'contest_submit_{contest_id}'))
    if voting_open and not has_finished_vote:
        kb.add(CallbackButton(text='🗳 Голосовать', payload=f'contest_vote_start_{contest_id}'))
    if voting_open and has_finished_vote:
        kb.add(CallbackButton(text='✅ Вы уже проголосовали', payload=f'contest_already_voted_{contest_id}'))
    kb.add(CallbackButton(text='🖼 Все работы', payload=f'contest_all_works_{contest_id}'))
    kb.add(CallbackButton(text='🔍 Найти работу по номеру', payload=f'contest_find_work_{contest_id}'))
    kb.add(CallbackButton(text='📋 Мои голоса', payload=f'contest_my_votes_{contest_id}'))
    kb.add(CallbackButton(text='📜 Правила конкурса', payload=f'contest_rules_{contest_id}'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))
    return kb.adjust(1).as_markup()


async def contests_kb(contests: list[Contest]):
    kb = InlineKeyboardBuilder()

    for contest in contests:
        kb.add(CallbackButton(text=f'{contest.description}', payload=f'contest_active_{contest.id}'))
    kb.add(CallbackButton(text='⬅ назад', payload='back_to_user_main'))
    return kb.adjust(1).as_markup()    



async def contest_categories_kb(contest_id):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='Все работы', payload=f'contest_cat_all_{contest_id}'))
    kb.add(CallbackButton(text='До 10 лет', payload=f'contest_cat_child_{contest_id}'))
    kb.add(CallbackButton(text='11–17 лет', payload=f'contest_cat_teen_{contest_id}'))
    kb.add(CallbackButton(text='18+', payload=f'contest_cat_adult_{contest_id}'))
    kb.add(CallbackButton(text='⬅ назад', payload=f'contest_active__{contest_id}'))
    return kb.adjust(2, 2, 1).as_markup()


async def contest_work_card_kb(work_id: int, is_selected: bool, is_last: bool, contest_id: int):
    kb = InlineKeyboardBuilder()
    if is_selected:
        kb.add(CallbackButton(text='☑ Выбрано', payload=f'contest_unselect_{work_id}'))
    else:
        kb.add(CallbackButton(text='❤️ Выбрать', payload=f'contest_select_{work_id}'))


    kb.add(CallbackButton(text='Пред ', payload=f'contest_vote_prev_{contest_id}'))

    if is_last:
        kb.add(CallbackButton(text='🏁 Завершить', payload=f'contest_vote_finish_{contest_id}'))
    else:
        kb.add(CallbackButton(text='➡️ След', payload=f'contest_vote_next_{contest_id}'))
    kb.add(CallbackButton(text='⏸ Вернуться позже', payload=f'contest_vote_pause_{contest_id}'))
    kb.add(CallbackButton(text='⬅️ Меню', payload='back_to_user_main'))
    return kb.adjust(1, 2, 1, 1).as_markup()


async def contest_vote_confirm_kb(contest_id):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='☑ Отправить', payload=f'contest_vote_submit_{contest_id}'))
    kb.add(CallbackButton(text='↩️ Продолжить просмотр', payload=f'contest_vote_resume_{contest_id}'))
    return kb.adjust(1).as_markup()


async def contest_vote_pause_kb(contest_id):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='▶️ Продолжить', payload=f'contest_vote_resume_{contest_id}'))
    kb.add(CallbackButton(text='⬅ назад', payload=f'contest_active_{contest_id}'))
    return kb.adjust(1).as_markup()


async def contest_submit_cancel_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='❌ Отменить', payload='contest_submit_cancel'))
    return kb.adjust(1).as_markup()


async def contest_submit_confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='✅ Подтверждаю', payload='contest_submit_confirm'))
    kb.add(CallbackButton(text='❌ Отменить', payload='contest_submit_cancel'))
    return kb.adjust(1).as_markup()


async def contest_back_kb(payload: str = 'client_contest'):
    kb = InlineKeyboardBuilder()
    kb.add(CallbackButton(text='⬅ назад', payload=payload))
    return kb.adjust(1).as_markup()
