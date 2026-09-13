"""add contest module

Revision ID: 0001_add_contest_module
Revises: 3d82278b297f
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001_add_contest_module'
down_revision: Union[str, None] = '3d82278b297f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('contests', sa.Column('title', sa.String(length=128), nullable=True))
    op.add_column('contests', sa.Column('rules', sa.String(length=2048), nullable=True))
    op.add_column('contests', sa.Column('submission_start', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contests', sa.Column('submission_end', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contests', sa.Column('voting_start', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contests', sa.Column('voting_end', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contests', sa.Column('voting_open', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('contests', sa.Column('results_published', sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_table(
        'contest_works',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('contest_id', sa.Integer(), sa.ForeignKey('contests.id'), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('author_name', sa.String(length=128), nullable=False),
        sa.Column('author_age', sa.Integer(), nullable=False),
        sa.Column('author_username', sa.String(length=128), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('category', sa.String(length=16), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('final_photo', sa.String(length=512), nullable=False),
        sa.Column('process_photo', sa.String(length=512), nullable=False),
        sa.Column('extra_photo', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('moderation_comment', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'contest_vote_sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('contest_id', sa.Integer(), sa.ForeignKey('contests.id'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('order_json', sa.String(length=8192), nullable=False),
        sa.Column('current_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('selected_json', sa.String(length=4096), nullable=False, server_default='[]'),
        sa.Column('is_finished', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'contest_votes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('contest_id', sa.Integer(), sa.ForeignKey('contests.id'), nullable=False),
        sa.Column('work_id', sa.Integer(), sa.ForeignKey('contest_works.id'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('contest_votes')
    op.drop_table('contest_vote_sessions')
    op.drop_table('contest_works')
    op.drop_column('contests', 'results_published')
    op.drop_column('contests', 'voting_open')
    op.drop_column('contests', 'voting_end')
    op.drop_column('contests', 'voting_start')
    op.drop_column('contests', 'submission_end')
    op.drop_column('contests', 'submission_start')
    op.drop_column('contests', 'rules')
    op.drop_column('contests', 'title')
