"""empty message

Revision ID: 8285dbf88423
Revises: 
Create Date: 2023-02-02 18:14:18.172722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8285dbf88423'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tables',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('limit', sa.Enum('MICRO_1', 'MICRO_2', name='tablelimit'), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tables'))
    )
    op.create_index(op.f('ix_tables_create_time'), 'tables', ['create_time'], unique=False)
    op.create_index(op.f('ix_tables_name'), 'tables', ['name'], unique=False)
    op.create_table('users',
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    op.create_table('game_histories',
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('table_id', sa.BigInteger(), nullable=True),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('state', sa.Enum('INITIAL', 'START', 'PREFLOP', 'FLOP', 'TURN', 'RIVER', 'SHOWDOWN', 'FINISHED', name='gamestate'), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['table_id'], ['tables.id'], name=op.f('fk_game_histories_table_id_tables')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_game_histories'))
    )
    op.create_index(op.f('ix_game_histories_create_time'), 'game_histories', ['create_time'], unique=False)
    op.create_index(op.f('ix_game_histories_state'), 'game_histories', ['state'], unique=False)
    op.create_table('seats',
    sa.Column('status', sa.Enum('FREE', 'RESERVED', 'IN_GAME', 'PLAYED', 'WAITING', name='seatstatus'), nullable=False),
    sa.Column('position', sa.Enum('UNKNOWN', 'SMALL_BLIND', 'BIG_BLIND', name='tablepositions'), nullable=False),
    sa.Column('number', sa.Enum('ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', name='seatnumber'), nullable=False),
    sa.Column('table_id', sa.BigInteger(), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['table_id'], ['tables.id'], name=op.f('fk_seats_table_id_tables'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_seats_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_seats'))
    )
    op.create_table('wallets',
    sa.Column('amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.Enum('USD', 'EUR', name='currency'), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_wallets_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_wallets'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wallets')
    op.drop_table('seats')
    op.drop_index(op.f('ix_game_histories_state'), table_name='game_histories')
    op.drop_index(op.f('ix_game_histories_create_time'), table_name='game_histories')
    op.drop_table('game_histories')
    op.drop_table('users')
    op.drop_index(op.f('ix_tables_name'), table_name='tables')
    op.drop_index(op.f('ix_tables_create_time'), table_name='tables')
    op.drop_table('tables')
    # ### end Alembic commands ###
