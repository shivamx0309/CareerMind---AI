"""add_postgresql_predicate_to_default_resume_index

Revision ID: 633bb4235e1e
Revises: a15558c0f59e
Create Date: 2026-11-10 11:36:16.646132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '633bb4235e1e'
down_revision: Union[str, Sequence[str], None] = 'a15558c0f59e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Safely replace index with dual SQLite & PostgreSQL partial index."""
    with op.batch_alter_table('resume_records', schema=None) as batch_op:
        batch_op.drop_index(
            'uq_profile_default_resume',
            sqlite_where=sa.text('is_default = 1'),
        )
        batch_op.create_index(
            'uq_profile_default_resume',
            ['career_profile_id'],
            unique=True,
            sqlite_where=sa.text('is_default = 1'),
            postgresql_where=sa.text('is_default IS TRUE'),
        )


def downgrade() -> None:
    """Revert index back to sqlite-only partial index."""
    with op.batch_alter_table('resume_records', schema=None) as batch_op:
        batch_op.drop_index(
            'uq_profile_default_resume',
            sqlite_where=sa.text('is_default = 1'),
            postgresql_where=sa.text('is_default IS TRUE'),
        )
        batch_op.create_index(
            'uq_profile_default_resume',
            ['career_profile_id'],
            unique=True,
            sqlite_where=sa.text('is_default = 1'),
        )
