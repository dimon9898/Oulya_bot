from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from dataclasses import dataclass

from app.database.models import Contest, User, Purchase


@dataclass
class UpdateContest:
    contest: Contest | None
    is_updated: bool




async def get_contest_status(db: AsyncSession):
    result = await db.scalars(select(Contest).where(Contest.id == 1))
    contest = result.first()

    if not contest:
        return 

    return contest


async def create_contest(db: AsyncSession) -> Contest:
    contest = Contest(
        title='Новый конкурс',
        description='Новый конкурс',
        enabled=False,
        voting_open=False,
    )
    db.add(contest)
    await db.commit()
    await db.refresh(contest)
    return contest


async def update_contest_state(db: AsyncSession, action: str, contest_id: int) -> Contest:
    result = await db.scalars(select(Contest).where(Contest.id == contest_id))
    contest = result.first()

    if not contest:
        return False

    if action == 'off':
        contest.enabled = False
    else:
        contest.enabled = True

    await db.commit()
    await db.refresh(contest)

    return contest


async def update_contest_title(db: AsyncSession, contest_id: int, title: str) -> UpdateContest:
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()

    if not contest:
         return UpdateContest(contest=None, is_updated=False)
    

    if contest.title != title:
        contest.title = title
        await db.commit()

    return UpdateContest(contest=contest, is_updated=True)




async def update_contest_description(db: AsyncSession, contest_id: int, description: str) -> UpdateContest:
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()

    if not contest:
         return UpdateContest(contest=None, is_updated=False)
    
    if contest.description != description:
        contest.description = description
        await db.commit()

    return UpdateContest(contest=contest, is_updated=True)

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

        
