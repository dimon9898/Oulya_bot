from datetime import datetime, timezone
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Contest, Course, CourseItem, Purchase

from app.create_paylink import create_payment_link


async def add_user(db: AsyncSession, user_id: int, came_from: str):
    result = await db.scalars(select(User).where(User.user_id == user_id))
    user = result.first()

    if user:
        return 
    
    new_user = User(
        user_id=user_id,
        came_from=came_from
    )
    db.add(new_user)
    await db.commit()

    return True


async def get_all_courses(db: AsyncSession, user_id: int):

    user_result = await db.scalars(select(User).where(User.user_id == user_id))
    user = user_result.first()

    if not user:
        raise  
    


    purchase_result = await db.scalars(select(Purchase.course_id)
                                       .where(Purchase.user_id == user.id)
                                       .where(Purchase.payment_status == 'payment.succeeded'))
    
    purchase_ids = purchase_result.all()

    if not purchase_ids:
        result = await db.scalars(select(Course).where(Course.is_active == True))
        courses = result.all()

        if not courses:
            return False
        
        return courses
    
    courses_result = await db.scalars(select(Course)
                                      .where(Course.id.not_in(purchase_ids))
                                      .where(Course.is_active == True))
    
    return courses_result.all()


async def get_course_info(db: AsyncSession, course_id: int):
    result = await db.scalars(select(Course).where(Course.id == course_id))
    course = result.first()

    return course



async def create_order(db: AsyncSession, course_id: int, user_id: int, email: str):
    user_result = await db.scalars(select(User).where(User.user_id == user_id))
    user = user_result.first()

    if not user:
        print('ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН')
        return False
    
    course_result = await db.scalars(select(Course).where(Course.id == course_id, Course.is_active == True))
    course = course_result.first()

    if not course:
        return False
    

    new_order = Purchase(
        user_id=user.id,
        course_id=course_id,
        price=course.price
    )
    db.add(new_order)

    try:
        await db.flush()
        payment = await create_payment_link(new_order.id, user_id, course_id, course.price, email)
    except Exception as e:
        print(f'Ошибка при создание платежа: {e}')
        await db.rollback()
        return False

    new_order.payment_id = payment.get('payment_id')

    await db.commit()
    await db.refresh(new_order)

    return payment


async def update_payment_status(db: AsyncSession, payment_id: str, payment_status: str) -> bool:
    result = await db.scalars(select(Purchase).where(Purchase.payment_id == payment_id))
    purchase = result.first()


    if not purchase:
        return False
    

    purchase.payment_status = payment_status
    purchase.paid_at = datetime.now(timezone.utc)

    await db.commit()
    return True


async def get_user_purchased_courses(db: AsyncSession, user_id: int):
    user_result = await db.scalars(select(User).where(User.user_id == user_id))
    user = user_result.first()

    if not user:
        raise  
    
    purchases_result = await db.scalars(select(Purchase)
                                        .options(selectinload(Purchase.course))
                                        .where(Purchase.user_id == user.id)
                                        .where(Purchase.payment_status == 'payment.succeeded'))
    purchases = purchases_result.all()

    if not purchases:
        return False
    
    return purchases



async def get_free_course(db: AsyncSession):
    result = await db.scalars(select(Course).where(Course.id == 1))
    course = result.first()

    if not course:
        return False
    
    return course


async def get_course_items(db: AsyncSession, course_id: int):
    result = await db.scalars(select(CourseItem)
                              .options(selectinload(CourseItem.course))
                              .where(CourseItem.category_id == course_id)
                              .order_by(CourseItem.id.asc()))
    
    course_items = result.all()
    
    return course_items



async def get_contest_info(db: AsyncSession):
    result = await db.scalars(select(Contest).where(Contest.id == 1))
    contest = result.first()

    if not contest:
        return False

    return contest