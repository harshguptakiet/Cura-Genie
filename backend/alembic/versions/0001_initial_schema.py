"""Initial database schema for CuraGenie

This migration creates the complete database schema including:
- Users and authentication
- Genomic data management
- PRS scores with duplicate prevention
- Timeline events
- Medical reports
- User sessions and password reset tokens

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema"""
    
    # Create enum types
    op.execute("""
        CREATE TYPE user_role_enum AS ENUM (
            'patient', 'doctor', 'admin'
        )
    """)
    
    op.execute("""
        CREATE TYPE processing_status_enum AS ENUM (
            'pending', 'processing', 'completed', 'failed'
        )
    """)
    
    op.execute("""
        CREATE TYPE file_type_enum AS ENUM (
            'vcf', 'fasta', 'bam', 'fastq', 'txt', 'csv'
        )
    """)
    
    op.execute("""
        CREATE TYPE risk_level_enum AS ENUM (
            'low', 'medium', 'high', 'very_high'
        )
    """)
    
    op.execute("""
        CREATE TYPE event_type_enum AS ENUM (
            'file_upload', 'analysis_complete', 'report_generated', 'prs_calculated'
        )
    """)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('patient', 'doctor', 'admin', name='user_role_enum'), nullable=False, default='patient'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create patient_profiles table
    op.create_table('patient_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('ethnicity', sa.String(length=100), nullable=True),
        sa.Column('medical_history', sa.Text(), nullable=True),
        sa.Column('family_history', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create genomic_data table
    op.create_table('genomic_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.Enum('vcf', 'fasta', 'bam', 'fastq', 'txt', 'csv', name='file_type_enum'), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='processing_status_enum'), nullable=False, default='pending'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create genomic_variants table
    op.create_table('genomic_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('genomic_data_id', sa.Integer(), nullable=False),
        sa.Column('chromosome', sa.String(length=10), nullable=False),
        sa.Column('position', sa.BigInteger(), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=False),
        sa.Column('alternative', sa.String(length=100), nullable=False),
        sa.Column('quality', sa.Float(), nullable=True),
        sa.Column('filter', sa.String(length=100), nullable=True),
        sa.Column('info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['genomic_data_id'], ['genomic_data.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('genomic_data_id', 'chromosome', 'position', 'reference', 'alternative', name='unique_variant_per_file')
    )
    
    # Create prs_scores table
    op.create_table('prs_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('genomic_data_id', sa.Integer(), nullable=False),
        sa.Column('disease_type', sa.String(length=100), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.Enum('low', 'medium', 'high', 'very_high', name='risk_level_enum'), nullable=False),
        sa.Column('percentile', sa.Float(), nullable=True),
        sa.Column('variants_used', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('algorithm_version', sa.String(length=50), nullable=True),
        sa.Column('reference_population', sa.String(length=100), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['genomic_data_id'], ['genomic_data.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'disease_type', 'genomic_data_id', name='unique_prs_per_user_disease_file')
    )
    
    # Create timeline_events table
    op.create_table('timeline_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.Enum('file_upload', 'analysis_complete', 'report_generated', 'prs_calculated', name='event_type_enum'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create medical_reports table
    op.create_table('medical_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('risk_factors', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token')
    )
    
    # Create password_reset_tokens table
    op.create_table('password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    
    # Create indexes for performance
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_active', 'users', ['is_active'])
    op.create_index('idx_users_role', 'users', ['role'])
    
    op.create_index('idx_patient_profiles_user', 'patient_profiles', ['user_id'])
    
    op.create_index('idx_genomic_data_user', 'genomic_data', ['user_id'])
    op.create_index('idx_genomic_data_status', 'genomic_data', ['status'])
    op.create_index('idx_genomic_data_uploaded', 'genomic_data', ['uploaded_at'])
    op.create_index('idx_genomic_data_type', 'genomic_data', ['file_type'])
    
    op.create_index('idx_genomic_variants_file', 'genomic_variants', ['genomic_data_id'])
    op.create_index('idx_genomic_variants_chromosome', 'genomic_variants', ['chromosome'])
    op.create_index('idx_genomic_variants_position', 'genomic_variants', ['position'])
    
    op.create_index('idx_prs_scores_user', 'prs_scores', ['user_id'])
    op.create_index('idx_prs_scores_disease', 'prs_scores', ['disease_type'])
    op.create_index('idx_prs_scores_risk', 'prs_scores', ['risk_level'])
    op.create_index('idx_prs_scores_calculated', 'prs_scores', ['calculated_at'])
    
    op.create_index('idx_timeline_events_user', 'timeline_events', ['user_id'])
    op.create_index('idx_timeline_events_type', 'timeline_events', ['event_type'])
    op.create_index('idx_timeline_events_created', 'timeline_events', ['created_at'])
    
    op.create_index('idx_medical_reports_user', 'medical_reports', ['user_id'])
    op.create_index('idx_medical_reports_type', 'medical_reports', ['report_type'])
    op.create_index('idx_medical_reports_generated', 'medical_reports', ['generated_at'])
    
    op.create_index('idx_user_sessions_user', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_token', 'user_sessions', ['session_token'])
    op.create_index('idx_user_sessions_expires', 'user_sessions', ['expires_at'])
    
    op.create_index('idx_password_reset_tokens_user', 'password_reset_tokens', ['user_id'])
    op.create_index('idx_password_reset_tokens_token', 'password_reset_tokens', ['token'])
    op.create_index('idx_password_reset_tokens_expires', 'password_reset_tokens', ['expires_at'])


def downgrade() -> None:
    """Drop all tables and types"""
    
    # Drop tables in reverse order
    op.drop_table('password_reset_tokens')
    op.drop_table('user_sessions')
    op.drop_table('medical_reports')
    op.drop_table('timeline_events')
    op.drop_table('prs_scores')
    op.drop_table('genomic_variants')
    op.drop_table('genomic_data')
    op.drop_table('patient_profiles')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS user_role_enum')
    op.execute('DROP TYPE IF EXISTS processing_status_enum')
    op.execute('DROP TYPE IF EXISTS file_type_enum')
    op.execute('DROP TYPE IF EXISTS risk_level_enum')
    op.execute('DROP TYPE IF EXISTS event_type_enum')
