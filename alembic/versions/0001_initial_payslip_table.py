"""Initial payslip table

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create payslips table
    op.create_table('payslips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('upload_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'month', 'year', name='uq_employee_month_year'),
        sa.UniqueConstraint('file_url')
    )
    
    # Create indexes
    op.create_index('ix_payslips_id', 'payslips', ['id'])
    op.create_index('ix_payslips_employee_id', 'payslips', ['employee_id'])
    op.create_index('ix_payslips_upload_timestamp', 'payslips', ['upload_timestamp'])
    op.create_index('ix_employee_year_month', 'payslips', ['employee_id', 'year', 'month'])
    op.create_index('ix_year_month', 'payslips', ['year', 'month'])
    op.create_index('ix_upload_timestamp_desc', 'payslips', [sa.text('upload_timestamp DESC')])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_upload_timestamp_desc', table_name='payslips')
    op.drop_index('ix_year_month', table_name='payslips')
    op.drop_index('ix_employee_year_month', table_name='payslips')
    op.drop_index('ix_payslips_upload_timestamp', table_name='payslips')
    op.drop_index('ix_payslips_employee_id', table_name='payslips')
    op.drop_index('ix_payslips_id', table_name='payslips')
    
    # Drop table
    op.drop_table('payslips')
