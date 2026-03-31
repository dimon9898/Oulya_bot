from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    await db.commit()
    await db.refresh(contest)

    return contest