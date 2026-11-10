"""create_learning_roadmaps_tables

Revision ID: b8963813309f
Revises: fbd615962846
Create Date: 2026-11-10 12:48:23.581053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8963813309f'
down_revision: Union[str, Sequence[str], None] = 'fbd615962846'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create learning roadmaps and associated tracking tables."""
    # 1. learning_roadmaps
    op.create_table(
        'learning_roadmaps',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('career_profile_id', sa.String(length=36), nullable=False),
        sa.Column('resume_record_id', sa.String(length=36), nullable=False),
        sa.Column('skill_gap_report_id', sa.String(length=36), nullable=False),
        sa.Column('target_role', sa.String(length=100), nullable=False),
        sa.Column('role_title', sa.String(length=150), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('weekly_study_hours', sa.Integer(), nullable=False),
        sa.Column('total_estimated_hours', sa.Float(), nullable=False),
        sa.Column('total_weeks', sa.Integer(), nullable=False),
        sa.Column('completed_topics_count', sa.Integer(), nullable=False),
        sa.Column('total_topics_count', sa.Integer(), nullable=False),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('weekly_schedule', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['career_profile_id'], ['career_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_record_id'], ['resume_records.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_gap_report_id'], ['skill_gap_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('learning_roadmaps', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_learning_roadmaps_career_profile_id'), ['career_profile_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_learning_roadmaps_resume_record_id'), ['resume_record_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_learning_roadmaps_skill_gap_report_id'), ['skill_gap_report_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_learning_roadmaps_target_role'), ['target_role'], unique=False)

    # 2. roadmap_skills
    op.create_table(
        'roadmap_skills',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('roadmap_id', sa.String(length=36), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('importance', sa.String(length=20), nullable=False),
        sa.Column('gap_type', sa.String(length=30), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('estimated_hours', sa.Float(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('prerequisites', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('practical_project', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['roadmap_id'], ['learning_roadmaps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('roadmap_skills', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_roadmap_skills_roadmap_id'), ['roadmap_id'], unique=False)

    # 3. roadmap_topics
    op.create_table(
        'roadmap_topics',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('roadmap_skill_id', sa.String(length=36), nullable=False),
        sa.Column('topic_name', sa.String(length=150), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('estimated_hours', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['roadmap_skill_id'], ['roadmap_skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('roadmap_topics', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_roadmap_topics_roadmap_skill_id'), ['roadmap_skill_id'], unique=False)

    # 4. learning_resources
    op.create_table(
        'learning_resources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('roadmap_topic_id', sa.String(length=36), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('is_free', sa.Boolean(), nullable=False),
        sa.Column('difficulty', sa.String(length=30), nullable=False),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['roadmap_topic_id'], ['roadmap_topics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('learning_resources', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_learning_resources_roadmap_topic_id'), ['roadmap_topic_id'], unique=False)

    # 5. roadmap_milestones
    op.create_table(
        'roadmap_milestones',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('roadmap_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['roadmap_id'], ['learning_roadmaps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('roadmap_milestones', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_roadmap_milestones_roadmap_id'), ['roadmap_id'], unique=False)


def downgrade() -> None:
    """Drop roadmap tables in reverse dependency order."""
    with op.batch_alter_table('roadmap_milestones', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_roadmap_milestones_roadmap_id'))
    op.drop_table('roadmap_milestones')

    with op.batch_alter_table('learning_resources', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_learning_resources_roadmap_topic_id'))
    op.drop_table('learning_resources')

    with op.batch_alter_table('roadmap_topics', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_roadmap_topics_roadmap_skill_id'))
    op.drop_table('roadmap_topics')

    with op.batch_alter_table('roadmap_skills', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_roadmap_skills_roadmap_id'))
    op.drop_table('roadmap_skills')

    with op.batch_alter_table('learning_roadmaps', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_learning_roadmaps_target_role'))
        batch_op.drop_index(batch_op.f('ix_learning_roadmaps_skill_gap_report_id'))
        batch_op.drop_index(batch_op.f('ix_learning_roadmaps_resume_record_id'))
        batch_op.drop_index(batch_op.f('ix_learning_roadmaps_career_profile_id'))
    op.drop_table('learning_roadmaps')
