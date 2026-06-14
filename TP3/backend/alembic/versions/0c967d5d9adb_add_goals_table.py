"""add goals table

Revision ID: 0c967d5d9adb
Revises: 38fc1f34cad0
Create Date: 2026-06-13 22:00:56.722591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0c967d5d9adb'
down_revision: Union[str, None] = '38fc1f34cad0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# categoryenum already exists in the DB (created by entries table migration)
categoryenum = postgresql.ENUM(
    'event', 'movie_series', 'book', 'city', 'place',
    name='categoryenum',
    create_type=False,
)


def upgrade() -> None:
    categoryenum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'goals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('category', categoryenum, nullable=False),
        sa.Column('target', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'year', 'category', name='uq_goal_user_year_category'),
    )


def downgrade() -> None:
    op.drop_table('goals')
    # do NOT drop categoryenum — it is still used by the entries table
