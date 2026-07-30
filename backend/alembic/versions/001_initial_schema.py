"""Initial schema migration for HireSmart AI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-07-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Recruiters Table
    op.create_table(
        'recruiters',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recruiters_email'), 'recruiters', ['email'], unique=True)
    op.create_index(op.f('ix_recruiters_id'), 'recruiters', ['id'], unique=False)

    # 2. Candidates Table
    op.create_table(
        'candidates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('education', sa.JSON(), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('projects', sa.JSON(), nullable=True),
        sa.Column('experience', sa.JSON(), nullable=True),
        sa.Column('certifications', sa.JSON(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('resume_pdf_path', sa.String(length=500), nullable=False),
        sa.Column('json_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidates_email'), 'candidates', ['email'], unique=False)
    op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)
    op.create_index(op.f('ix_candidates_name'), 'candidates', ['name'], unique=False)

    # 3. Job Descriptions Table
    op.create_table(
        'job_descriptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('role', sa.String(length=255), nullable=False),
        sa.Column('raw_description', sa.Text(), nullable=False),
        sa.Column('required_skills', sa.JSON(), nullable=True),
        sa.Column('experience_required', sa.String(length=255), nullable=True),
        sa.Column('education_required', sa.String(length=255), nullable=True),
        sa.Column('preferred_tech', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_descriptions_id'), 'job_descriptions', ['id'], unique=False)
    op.create_index(op.f('ix_job_descriptions_role'), 'job_descriptions', ['role'], unique=False)

    # 4. Analysis Results Table
    op.create_table(
        'analysis_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('job_description_id', sa.Integer(), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=False),
        sa.Column('missing_skills', sa.JSON(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('recommendation', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_description_id'], ['job_descriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_results_id'), 'analysis_results', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_analysis_results_id'), table_name='analysis_results')
    op.drop_table('analysis_results')
    op.drop_index(op.f('ix_job_descriptions_role'), table_name='job_descriptions')
    op.drop_index(op.f('ix_job_descriptions_id'), table_name='job_descriptions')
    op.drop_table('job_descriptions')
    op.drop_index(op.f('ix_candidates_name'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_id'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_email'), table_name='candidates')
    op.drop_table('candidates')
    op.drop_index(op.f('ix_recruiters_id'), table_name='recruiters')
    op.drop_index(op.f('ix_recruiters_email'), table_name='recruiters')
    op.drop_table('recruiters')
