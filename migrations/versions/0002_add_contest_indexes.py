"""add contest unique indexes

Revision ID: 0002_add_contest_indexes
Revises: 0001_add_contest_module
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '0002_add_contest_indexes'
down_revision: Union[str, None] = '0001_add_contest_module'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # один голос на пару (конкурс, работа, пользователь)
    op.create_index(
        'uq_contest_votes_contest_work_user',
        'contest_votes',
        ['contest_id', 'work_id', 'user_id'],
        unique=True,
    )
    # одна сессия голосования на пользователя в рамках конкурса
    op.create_index(
        'uq_contest_vote_sessions_contest_user',
        'contest_vote_sessions',
        ['contest_id', 'user_id'],
        unique=True,
    )
    # уникальный номер работы внутри конкурса
    op.create_index(
        'uq_contest_works_contest_number',
        'contest_works',
        ['contest_id', 'number'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('uq_contest_works_contest_number', table_name='contest_works')
    op.drop_index('uq_contest_vote_sessions_contest_user', table_name='contest_vote_sessions')
    op.drop_index('uq_contest_votes_contest_work_user', table_name='contest_votes')
