"""create_skill_gap_reports_table

Revision ID: fbd615962846
Revises: 633bb4235e1e
Create Date: 2026-11-10 11:49:52.039552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbd615962846'
down_revision: Union[str, Sequence[str], None] = '633bb4235e1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create skill_gap_reports table."""
    op.create_table(
        'skill_gap_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('career_profile_id', sa.String(length=36), nullable=False),
        sa.Column('resume_record_id', sa.String(length=36), nullable=False),
        sa.Column('target_role', sa.String(length=100), nullable=False),
        sa.Column('role_title', sa.String(length=150), nullable=False),
        sa.Column('benchmark_version', sa.String(length=20), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('required_coverage_percentage', sa.Float(), nullable=True),
        sa.Column('preferred_coverage_percentage', sa.Float(), nullable=True),
        sa.Column('total_required_skills', sa.Integer(), nullable=False),
        sa.Column('matched_required_skills_count', sa.Integer(), nullable=False),
        sa.Column('related_required_skills_count', sa.Integer(), nullable=False),
        sa.Column('missing_required_skills_count', sa.Integer(), nullable=False),
        sa.Column('total_preferred_skills', sa.Integer(), nullable=False),
        sa.Column('matched_preferred_skills_count', sa.Integer(), nullable=False),
        sa.Column('related_preferred_skills_count', sa.Integer(), nullable=False),
        sa.Column('missing_preferred_skills_count', sa.Integer(), nullable=False),
        sa.Column('matched_skills', sa.JSON(), nullable=False),
        sa.Column('related_skills', sa.JSON(), nullable=False),
        sa.Column('missing_required_skills', sa.JSON(), nullable=False),
        sa.Column('missing_preferred_skills', sa.JSON(), nullable=False),
        sa.Column('category_breakdown', sa.JSON(), nullable=False),
        sa.Column('analysis_status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['career_profile_id'], ['career_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_record_id'], ['resume_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('skill_gap_reports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_skill_gap_reports_career_profile_id'), ['career_profile_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_skill_gap_reports_resume_record_id'), ['resume_record_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_skill_gap_reports_target_role'), ['target_role'], unique=False)


def downgrade() -> None:
    """Drop skill_gap_reports table."""
    with op.batch_alter_table('skill_gap_reports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_skill_gap_reports_target_role'))
        batch_op.drop_index(batch_op.f('ix_skill_gap_reports_resume_record_id'))
        batch_op.drop_index(batch_op.f('ix_skill_gap_reports_career_profile_id'))

    op.drop_table('skill_gap_reports')
