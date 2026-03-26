from maxapi.types import MessageCreated, MessageCallback, BotStarted
from maxapi import Router, F
from maxapi.types.attachments.upload import AttachmentPayload, AttachmentUpload
from maxapi.types.attachments.image import AttachmentType, Image
from maxapi.types.attachments.video import Video
from maxapi.enums.upload_type import UploadType
from maxapi.enums.parse_mode import ParseMode
from maxapi.exceptions.max import MaxApiError
from maxapi.filters.command import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.repository.requests as rq

import app.keyboards.user_kb as kb
from config import settings
from deeplink_gen import Deeplink


user = Router()


@user.bot_started()
async def bot_created(event: BotStarted, session: AsyncSession):
    payload = event.payload

    if payload:
        came_from = Deeplink.decode(payload)
    else:
        came_from = 'direct'    

    await rq.add_user(session, event.from_user.user_id, came_from)
    await send_welcome(event.chat_id, event.bot)

@user.message_created(CommandStart())
async def cmd_start(msg: MessageCreated):
    await send_welcome(msg.chat.chat_id, msg.bot)


async def send_welcome(chat_id, bot):
    await bot.send_message(chat_id=chat_id, text='👋 Привет!\n\n'
                                        'Рада, что ты здесь — значит, наш набор уже у тебя в руках 🎁\n\n'
                                        'Этот бот — твой помощник по творчеству:\n\n'
                                        '🎨 Видео и фото мастер-классы\n'
                                        '📚 Курсы для тех, кто хочет большего\n'
                                        '🏆 Ежемесячные конкурсы с призами\n'
                                        '🛍 Всё, что нужно для поделок\n\n'
                                        'Начни с бесплатного урока — он уже ждёт тебя 👇',
                                        attachments=[
                                                    Image(
                                                        type=AttachmentType.IMAGE,
                                                        payload=AttachmentUpload(
                                                            type=UploadType.IMAGE,
                                                            payload=AttachmentPayload(token=settings.LOGO_ID)
                                                        )
                                                    ),
                                                    await kb.user_start_kb()
                                                ])

@user.message_callback(F.callback.payload == 'user_start')
async def start_handler(event: MessageCallback):
    await event.message.delete()
    await event.bot.send_message(chat_id=event.chat.chat_id, text='👋 Привет!\n\n'
                                            'Рада, что ты здесь — значит, наш набор уже у тебя в руках 🎁\n\n'
                                            'Этот бот — твой помощник по творчеству:\n\n'
                                            '🎨 Видео и фото мастер-классы\n'
                                            '📚 Курсы для тех, кто хочет большего\n'
                                            '🏆 Ежемесячные конкурсы с призами\n'
                                            '🛍 Всё, что нужно для поделок\n\n'
                                            'Начни с бесплатного урока — он уже ждёт тебя 👇',
                                            attachments=[
                                                await kb.user_main_kb()
                                            ])


@user.message_callback(F.callback.payload == 'back_to_user_main')
async def back_to_user_main(event: MessageCallback):
    await start_handler(event)








@user.message_callback(F.callback.payload == 'whats_in_the_chanel')
async def whats_in_the_chanel(event: MessageCallback):
    await event.message.delete()
    await event.bot.send_message(chat_id=event.chat.chat_id, text='<b>🎨 Что в канале ?</b>\n\n'
                                            '🌸 В нашем канале — всё для тех, кто\n'
                                            'любит творить своими руками!\n\n'
                                            '✂ Пошаговые фото-инструкции\n'
                                            '🎬 Видео мастер-классы\n'
                                            '💡 Идеи для поделок с детьми\n'
                                            '🏆 Конкурсы с подарками каждый\n'
                                            'месяц\n\n'
                                            'Уже 1000+ мастериц читают нас\n'
                                            'каждый день 🤍',
                                            parse_mode=ParseMode.HTML,    
                                            attachments=[
                                                await kb.what_is_chanel_kb()
                                            ])


@user.message_callback(F.callback.payload == 'client_free_lesson')
async def client_free_lesson(event: MessageCallback):
    await event.message.delete()
    member = await event.bot.get_chat_member(chat_id=settings.CHANEL_ID, user_id=event.from_user.user_id)
    if member is None:
        await event.message.answer('<b>🎁 Бесплатный урок</b>\n\n'
                                        '🎁 Держи подарок от нас!\n\n'
                                        'Специально для тех, кто только что\n'
                                        'открыл наш набор — бесплатный\n'
                                        'мастер-класс в подарок 🎨\n\n'
                                        '‼️ <b>Чтобы получить урок, подпишись на</b>\n'
                                        '<b>канал и нажми на кнопку</b>\n'
                                        '<b>"✅ Я подписался"</b>',
                                        attachments=[
                                            await kb.client_free_sign_subscription_kb()
                                        ])
    else:
        await event.message.answer('<b>🎁 Бесплатный урок</b>\n\n'
                                        '🎁 Держи подарок от нас!\n\n'
                                        'Специально для тех, кто только что\n'
                                        'открыл наш набор — бесплатный\n'
                                        'мастер-класс в подарок 🎨')
    



@user.message_callback(F.callback.payload == 'client_free_check_subscription')
async def client_course_check_subscription(event: MessageCallback):
    member = await event.bot.get_chat_member(chat_id=settings.CHANEL_ID, user_id=event.from_user.user_id)
    if member is None:
        await event.message.delete()
        await event.message.answer('❌ Чтобы открыть бесплатный урок необходимо подписаться на канал',
                                   attachments=[
                                       await kb.client_free_sign_subscription_kb()
                                   ])
        return
    
    await client_free_lesson(event)




@user.message_callback(F.callback.payload == 'client_paid_courses')
async def client_paid_courses(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    courses = await rq.get_all_courses(session)
    
    member = await event.bot.get_chat_member(
        chat_id=settings.CHANEL_ID, 
        user_id=event.from_user.user_id
    )
    if member is None:
        await event.message.answer(
            'Для начало подпишитесь на наш канал',
            attachments=[await kb.client_courses_sign_subscription_kb()]
        )
        return
    
    if courses:
        response = ('📚 Наши курсы по рукоделию\n\n'
                    'Для тех, кто хочет научиться по-\n'
                    'настоящему — не просто повторить, а\n'
                    'понять и создавать самой 🌿')
    else:
        response = ('Нет актуальных курсов!')
    
    await event.message.answer(
        text=response,
        attachments=[await kb.client_courses_list_kb(courses)]
    )


@user.message_callback(F.callback.payload.startswith('client_course_'))
async def client_course_info(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    course_id = int(event.callback.payload.split('_')[2])
    course = await rq.get_course_info(session, course_id)

    if course.description == 'null':
        course_text = (f'💠 Название: <b>{course.title}</b>\n\n'
                    f'💳 Цена: <b>{course.price}</b> руб.')            
    
    else:
        course_text = (f'💠 Название: <b>{course.title}</b>\n\n'
                    f'💠 Описание: <b>{course.description}</b>\n\n'   
                    f'💳 Цена: <b>{course.price}</b> руб.') 

    if course.photo_type == 'jpg':
        await event.message.answer(text=course_text, 
                                   attachments=[
                                       await kb.course_buy_kb(course_id),
                                       AttachmentUpload(
                                           type=UploadType.IMAGE,
                                           payload=course.photo_url
                                       )
                                   ],
                                  parse_mode=ParseMode.HTML)
        return
    
    if course.photo_type == 'gif':
        await event.message.answer(text=course_text, 
                                   attachments=[
                                        await kb.course_buy_kb(course_id),
                                        AttachmentUpload(
                                             type=UploadType.VIDEO,
                                             payload=AttachmentPayload(token=course.photo_url)
                                        )
                                   ],  parse_mode=ParseMode.HTML)   
        return
    
    if course.photo_type == 'nul':
        await event.message.answer(text=course_text, 
                                   attachments=[
                                       await kb.course_kb(course_id)
                                   ],
                                      parse_mode=ParseMode.HTML)



@user.message_callback(F.callback.payload.startswith('click_buy_course_'))
async def click_buy_course_func(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    course_id = int(event.callback.payload.split('_')[3])
    user_id = event.from_user.user_id
    payment = await rq.create_order(session, course_id, user_id)
    payment_url = payment['confirmation_url']
    await event.message.answer(text='🔗 <b>Ссылка для оплаты...</b> ⬇️\n\n'
            f'<a href="{payment_url}">Перейти к оплате</a> 💳\n\n'
            '👉🏻 <i>Пожалуйста, завершите оплату по указанной ссылке.</i>', parse_mode=ParseMode.HTML)












@user.message_callback(F.callback.payload == 'client_shop')
async def client_shop_func(event: MessageCallback):
    await event.message.delete()
    await event.message.answer(text='🛍 Наши магазины на маркетплейсах\n\n'
                                    'Все материалы, которые мы используем\n'
                                    'в уроках — можно купить у нас!\n\n'
                                    '✨ Подпишись на канал — там мы\n'
                                    'анонсируем новинки и скидки первыми!',
                               attachments=[
                                   await kb.shop_kbs()
                               ])


@user.message_callback(F.callback.payload == 'client_social_site')
async def client_social_site_func(event: MessageCallback):
    await event.message.delete()
    await event.message.answer(text='<b>📱 Соц сети</b>',
                               attachments=[
                                   await kb.social_kbs()
                               ], parse_mode=ParseMode.HTML)


@user.message_created()
async def get_url_photo(msg: MessageCreated):
    attachments = msg.message.body.attachments
    if not attachments:
        return 


    for attachment in attachments:
        if isinstance(attachment, Image):
            file_id = attachment.payload.token
            await msg.message.answer(text=f'{file_id}')

        if isinstance(attachment, Video):
                file_id = attachment.payload.token
                await msg.message.answer(text=f'{file_id}')        