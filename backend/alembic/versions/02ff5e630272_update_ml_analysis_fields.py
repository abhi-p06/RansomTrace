"""update_ml_analysis_fields

Revision ID: 02ff5e630272
Revises: a52a80d48337
Create Date: 2026-10-06 00:06:42.379188

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02ff5e630272'
down_revision: Union[str, Sequence[str], None] = 'a52a80d48337'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    # Recreate or update ml_analyses
    if 'ml_analyses' not in tables:
        op.create_table(
            'ml_analyses',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('case_id', sa.String(length=36), nullable=True),
            sa.Column('wallet_id', sa.String(length=36), nullable=True),
            sa.Column('wallet_address', sa.String(length=128), nullable=True),
            sa.Column('model_name', sa.String(length=100), nullable=False),
            sa.Column('model_version', sa.String(length=50), nullable=False),
            sa.Column('raw_anomaly_score', sa.Float(), nullable=False),
            sa.Column('normalized_score', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('classification', sa.String(length=50), nullable=False, server_default='NORMAL'),
            sa.Column('is_anomaly', sa.Boolean(), nullable=False),
            sa.Column('features_used', sa.JSON(), nullable=True),
            sa.Column('feature_contributions', sa.JSON(), nullable=True),
            sa.Column('explanation', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['case_id'], ['investigation_cases.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_ml_analyses_wallet_address'), 'ml_analyses', ['wallet_address'], unique=False)
        op.create_index(op.f('ix_ml_analyses_case_id'), 'ml_analyses', ['case_id'], unique=False)
        op.create_index(op.f('ix_ml_analyses_wallet_id'), 'ml_analyses', ['wallet_id'], unique=False)
    else:
        with op.batch_alter_table('ml_analyses') as batch_op:
            batch_op.add_column(sa.Column('wallet_address', sa.String(length=128), nullable=True))
            batch_op.add_column(sa.Column('normalized_score', sa.Float(), nullable=False, server_default='0.0'))
            batch_op.add_column(sa.Column('classification', sa.String(length=50), nullable=False, server_default='NORMAL'))
            batch_op.add_column(sa.Column('features_used', sa.JSON(), nullable=True))
            batch_op.add_column(sa.Column('explanation', sa.Text(), nullable=True))
            batch_op.alter_column('case_id', existing_type=sa.VARCHAR(length=36), nullable=True)
            batch_op.create_index(batch_op.f('ix_ml_analyses_wallet_address'), ['wallet_address'], unique=False)

    # Recreate or update risk_assessments
    if 'risk_assessments' not in tables:
        op.create_table(
            'risk_assessments',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('case_id', sa.String(length=36), nullable=True),
            sa.Column('wallet_id', sa.String(length=36), nullable=True),
            sa.Column('wallet_address', sa.String(length=128), nullable=True),
            sa.Column('risk_score', sa.Float(), nullable=False),
            sa.Column('risk_tier', sa.String(length=50), nullable=False),
            sa.Column('heuristics_summary', sa.JSON(), nullable=True),
            sa.Column('disclaimer', sa.Text(), nullable=False),
            sa.Column('assessed_by', sa.String(length=100), nullable=False),
            sa.ForeignKeyConstraint(['case_id'], ['investigation_cases.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_risk_assessments_wallet_address'), 'risk_assessments', ['wallet_address'], unique=False)
        op.create_index(op.f('ix_risk_assessments_case_id'), 'risk_assessments', ['case_id'], unique=False)
        op.create_index(op.f('ix_risk_assessments_wallet_id'), 'risk_assessments', ['wallet_id'], unique=False)
    else:
        with op.batch_alter_table('risk_assessments') as batch_op:
            batch_op.add_column(sa.Column('wallet_address', sa.String(length=128), nullable=True))
            batch_op.alter_column('case_id', existing_type=sa.VARCHAR(length=36), nullable=True)
            batch_op.create_index(batch_op.f('ix_risk_assessments_wallet_address'), ['wallet_address'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('risk_assessments')
    op.drop_table('ml_analyses')
