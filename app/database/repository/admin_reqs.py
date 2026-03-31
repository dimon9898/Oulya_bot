from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.database.models import Contest, User, Purchase


async def get_contest_status(db: AsyncSession):
    result = await db.scalars(select(Contest).where(Contest.id == 1))
    contest = result.first()

    if not contest:
        return 

    return contest


async def update_contest_state(db: AsyncSession, action: str) -> bool:
    result = await db.scalars(select(Contest).where(Contest.id == 1))
    contest = result.first()

    if not contest:
        return False
    
    if action == 'off':
        contest.enabled = False
        await db.commit()
        await db.refresh(contest)
        return contest
    
    contest.description = action
    contest.enabled = True

    await db.commit()
    await db.refresh(contest)

    return contest


async def get_statistics_bot(db: AsyncSession):
        result = await db.execute(select(func.count(User.id)).where(User.is_active == True))
        count = result.scalar() or 0
        
        stmt = await db.execute(select(func.coalesce(func.sum(Purchase.price), 0))
                                .where(Purchase.payment_status == 'payment.succeeded'))
        total_sum = stmt.scalar()
        
        week_ago = datetime.now() - timedelta(days=7)
        new_users_stmt = await db.execute(select(func.count(User.id)).where(User.create_at >= week_ago))
        new_users = new_users_stmt.scalar() or 0
        
        pay_count = await db.execute(select(func.count(Purchase.id)).where(Purchase.payment_status == 'payment.succeeded'))
        payment_count = pay_count.scalar() or 0

        sources_stmt = await db.execute(select(User.came_from, func.count(User.id))
                                             .group_by(User.came_from)
                                             .order_by(func.count(User.id).desc())
                                             )
        sources = dict(sources_stmt.all())

        return {'count': count, 'total_sum': total_sum, 'new_users': new_users, 'payment_count': payment_count, 'sources': sources}

        
