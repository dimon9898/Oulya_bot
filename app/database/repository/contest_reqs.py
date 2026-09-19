import json
import random
from datetime import datetime, timezone
from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Contest, ContestWork, ContestVote, ContestVoteSession
from logger_init import logger


CATEGORY_LABELS = {
    'child': 'до 10 лет',
    'teen': '11–17 лет',
    'adult': '18+',
}

STATUS_LABELS = {
    'pending': 'На проверке',
    'approved': 'Допущена',
    'need_proof': 'Нужно подтверждение',
    'rejected': 'Отклонена',
}


def detect_category(age: int) -> str:
    if age <= 10:
        return 'child'
    if age <= 17:
        return 'teen'
    return 'adult'


async def get_active_contest(db: AsyncSession) -> Contest | None:
    result = await db.scalars(select(Contest)
                              .options(selectinload(Contest.works))
                              .where(Contest.id == 1))
    return result.first()


async def get_contest_by_id(db: AsyncSession, contest_id: int) -> Contest | None:
    result = await db.scalars(select(Contest).where(Contest.id == contest_id))
    return result.first()


def _as_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_submission_open(contest: Contest | None) -> bool:
    if not contest or not contest.enabled:
        return False
    now = datetime.now(timezone.utc)
    start = _as_aware(contest.submission_start)
    end = _as_aware(contest.submission_end)
    if start and now < start:
        return False
    if end and now > end:
        return False
    return True


def is_voting_open(contest: Contest | None) -> bool:
    if not contest or not contest.voting_open:
        return False
    now = datetime.now(timezone.utc)
    start = _as_aware(contest.voting_start)
    end = _as_aware(contest.voting_end)
    if start and now < start:
        return False
    if end and now > end:
        return False
    return True


async def get_next_work_number(db: AsyncSession, contest_id: int) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(ContestWork.number), 0))
        .where(ContestWork.contest_id == contest_id)
    )
    return (result.scalar() or 0) + 1


async def create_work(
    db: AsyncSession,
    contest_id: int,
    user_id: int,
    author_name: str,
    author_age: int,
    author_username: str,
    title: str,
    description: str,
    final_photo: str,
    process_photo: str,
) -> ContestWork | None:
    try:
        number = await get_next_work_number(db, contest_id)
        work = ContestWork(
            contest_id=contest_id,
            number=number,
            user_id=user_id,
            author_name=author_name,
            author_age=author_age,
            author_username=author_username,
            category=detect_category(author_age),
            title=title,
            description=description,
            final_photo=final_photo,
            process_photo=process_photo,
            status='pending',
        )
        db.add(work)
        await db.commit()
        await db.refresh(work)
        return work
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(f'Ошибка при создании работы конкурса: {exc}')
        return None


async def get_works_by_status(
    db: AsyncSession,
    contest_id: int,
    status: str | None = None,
    offset: int = 0,
    limit: int = 5,
) -> list[ContestWork]:
    stmt = select(ContestWork).where(ContestWork.contest_id == contest_id)
    if status:
        stmt = stmt.where(ContestWork.status == status)
    stmt = stmt.order_by(ContestWork.number.asc()).offset(offset).limit(limit)
    result = await db.scalars(stmt)
    return list(result.all())


async def count_works(db: AsyncSession, contest_id: int, status: str | None = None) -> int:
    stmt = select(func.count(ContestWork.id)).where(ContestWork.contest_id == contest_id)
    if status:
        stmt = stmt.where(ContestWork.status == status)
    result = await db.execute(stmt)
    return result.scalar() or 0


async def get_work_by_id(db: AsyncSession, work_id: int) -> ContestWork | None:
    result = await db.scalars(select(ContestWork).where(ContestWork.id == work_id))
    return result.first()


async def get_work_by_number(db: AsyncSession, contest_id: int, number: int) -> ContestWork | None:
    result = await db.scalars(
        select(ContestWork)
        .where(ContestWork.contest_id == contest_id)
        .where(ContestWork.number == number)
    )
    return result.first()


async def update_work_status(
    db: AsyncSession,
    work_id: int,
    status: str,
    comment: str | None = None,
) -> ContestWork | None:
    work = await get_work_by_id(db, work_id)
    if not work:
        return None
    work.status = status
    if comment is not None:
        work.moderation_comment = comment
    await db.commit()
    await db.refresh(work)
    return work


async def get_approved_works(db: AsyncSession, contest_id: int) -> list[ContestWork]:
    result = await db.scalars(
        select(ContestWork)
        .where(ContestWork.contest_id == contest_id)
        .where(ContestWork.status == 'approved')
        .order_by(ContestWork.number.asc())
    )
    return list(result.all())


async def get_approved_works_by_category(
    db: AsyncSession,
    contest_id: int,
    category: str,
) -> list[ContestWork]:
    result = await db.scalars(
        select(ContestWork)
        .where(ContestWork.contest_id == contest_id)
        .where(ContestWork.status == 'approved')
        .where(ContestWork.category == category)
        .order_by(ContestWork.number.asc())
    )
    return list(result.all())


async def get_vote_session(
    db: AsyncSession,
    contest_id: int,
    user_id: int,
) -> ContestVoteSession | None:
    result = await db.scalars(
        select(ContestVoteSession)
        .where(ContestVoteSession.contest_id == contest_id)
        .where(ContestVoteSession.user_id == user_id)
    )
    return result.first()


async def create_vote_session(
    db: AsyncSession,
    contest_id: int,
    user_id: int,
    work_ids: list[int],
) -> ContestVoteSession | None:
    try:
        random.shuffle(work_ids)
        session = ContestVoteSession(
            contest_id=contest_id,
            user_id=user_id,
            order_json=json.dumps(work_ids),
            current_index=0,
            selected_json='[]',
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(f'Ошибка при создании сессии голосования: {exc}')
        return None


async def update_vote_session(
    db: AsyncSession,
    session: ContestVoteSession,
    current_index: int | None = None,
    selected: list[int] | None = None,
    is_finished: bool | None = None,
) -> ContestVoteSession:
    if current_index is not None:
        session.current_index = current_index
    if selected is not None:
        session.selected_json = json.dumps(selected)
    if is_finished is not None:
        session.is_finished = is_finished
    await db.commit()
    await db.refresh(session)
    return session


def get_session_order(session: ContestVoteSession) -> list[int]:
    try:
        return json.loads(session.order_json or '[]')
    except (ValueError, TypeError):
        return []


def get_session_selected(session: ContestVoteSession) -> list[int]:
    try:
        return json.loads(session.selected_json or '[]')
    except (ValueError, TypeError):
        return []


async def has_finished_vote(db: AsyncSession, contest_id: int, user_id: int) -> bool:
    result = await db.scalars(
        select(ContestVoteSession)
        .where(ContestVoteSession.contest_id == contest_id)
        .where(ContestVoteSession.user_id == user_id)
        .where(ContestVoteSession.is_finished == True)
    )
    return result.first() is not None


async def save_votes(
    db: AsyncSession,
    contest_id: int,
    user_id: int,
    work_ids: list[int],
) -> bool:
    try:
        for work_id in work_ids:
            db.add(ContestVote(
                contest_id=contest_id,
                work_id=work_id,
                user_id=user_id,
            ))
        await db.commit()
        return True
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(f'Ошибка при сохранении голосов: {exc}')
        return False


async def get_user_votes(
    db: AsyncSession,
    contest_id: int,
    user_id: int,
) -> list[ContestWork]:
    result = await db.scalars(
        select(ContestWork)
        .join(ContestVote, ContestVote.work_id == ContestWork.id)
        .where(ContestVote.contest_id == contest_id)
        .where(ContestVote.user_id == user_id)
        .order_by(ContestWork.number.asc())
    )
    return list(result.all())


async def get_results(db: AsyncSession, contest_id: int) -> dict:
    stmt = (
        select(ContestWork, func.count(ContestVote.id).label('votes_count'))
        .outerjoin(ContestVote, ContestVote.work_id == ContestWork.id)
        .where(ContestWork.contest_id == contest_id)
        .where(ContestWork.status == 'approved')
        .group_by(ContestWork.id)
        .order_by(func.count(ContestVote.id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    by_category: dict[str, list] = {'child': [], 'teen': [], 'adult': []}
    for work, votes_count in rows:
        by_category.setdefault(work.category, []).append((work, votes_count))

    return {
        'all': rows,
        'by_category': by_category,
    }


async def set_voting_open(db: AsyncSession, contest_id: int, is_open: bool) -> bool:
    contest = await get_contest_by_id(db, contest_id)
    if not contest:
        return False
    contest.voting_open = is_open
    await db.commit()
    return True


async def set_results_published(db: AsyncSession, contest_id: int, published: bool) -> bool:
    contest = await get_contest_by_id(db, contest_id)
    if not contest:
        return False
    contest.results_published = published
    await db.commit()
    return True


async def update_contest_dates(
    db: AsyncSession,
    contest_id: int,
    submission_start: datetime | None = None,
    submission_end: datetime | None = None,
    voting_start: datetime | None = None,
    voting_end: datetime | None = None,
) -> bool:
    contest = await get_contest_by_id(db, contest_id)
    if not contest:
        return False
    if submission_start is not None:
        contest.submission_start = submission_start
    if submission_end is not None:
        contest.submission_end = submission_end
    if voting_start is not None:
        contest.voting_start = voting_start
    if voting_end is not None:
        contest.voting_end = voting_end
    await db.commit()
    return True
