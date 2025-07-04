"""initial

Revision ID: 64354bc3ccf5
Revises: 
Create Date: 2025-07-02 10:11:35.662420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64354bc3ccf5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('core_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_core_users_email'), 'core_users', ['email'], unique=True)
    op.create_index(op.f('ix_core_users_id'), 'core_users', ['id'], unique=False)
    op.create_table('organizations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('database_name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('database_name')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    op.create_table('tenant_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('avatar', sa.String(length=500), nullable=True),
    sa.Column('bio', sa.String(length=1000), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenant_users_email'), 'tenant_users', ['email'], unique=True)
    op.create_index(op.f('ix_tenant_users_id'), 'tenant_users', ['id'], unique=False)
    op.create_table('organization_owners',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['core_users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'organization_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('organization_owners')
    op.drop_index(op.f('ix_tenant_users_id'), table_name='tenant_users')
    op.drop_index(op.f('ix_tenant_users_email'), table_name='tenant_users')
    op.drop_table('tenant_users')
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
    op.drop_index(op.f('ix_core_users_id'), table_name='core_users')
    op.drop_index(op.f('ix_core_users_email'), table_name='core_users')
    op.drop_table('core_users')
    # ### end Alembic commands ###
