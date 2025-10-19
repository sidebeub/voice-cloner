"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-10-19 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create voice_profiles table
    op.create_table('voice_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sample_audio_path', sa.String(length=500), nullable=True),
        sa.Column('model_path', sa.String(length=500), nullable=True),
        sa.Column('is_trained', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_voice_profiles_id'), 'voice_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_voice_profiles_name'), 'voice_profiles', ['name'], unique=False)

    # Create generated_audio table
    op.create_table('generated_audio',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('voice_profile_id', sa.Integer(), nullable=True),
        sa.Column('text_input', sa.Text(), nullable=False),
        sa.Column('audio_path', sa.String(length=500), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('settings', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_audio_id'), 'generated_audio', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_generated_audio_id'), table_name='generated_audio')
    op.drop_table('generated_audio')
    op.drop_index(op.f('ix_voice_profiles_name'), table_name='voice_profiles')
    op.drop_index(op.f('ix_voice_profiles_id'), table_name='voice_profiles')
    op.drop_table('voice_profiles')
