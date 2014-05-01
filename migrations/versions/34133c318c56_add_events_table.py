"""add events table

Revision ID: 34133c318c56
Revises: 1710dfa54dbd
Create Date: 2014-02-08 16:04:20.919954

"""

# revision identifiers, used by Alembic.
revision = '34133c318c56'
down_revision = '1710dfa54dbd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('race_id', sa.Integer(), nullable=True),
    sa.Column('player', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Numeric(precision=7, scale=1), nullable=True),
    sa.Column('lap', sa.Integer(), nullable=True),
    sa.Column('event_type', sa.Enum('Lap', 'Item', 'Collision', 'Pass', 'Shortcut', 'Tag', 'Fall', 'Reverse', name='event_type'), nullable=True),
    sa.Column('event_subtype', sa.String(), nullable=True),
    sa.Column('event_info', sa.String(), nullable=True),
    sa.Column('linked_event_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.VARCHAR(length=1024), nullable=True),
    sa.ForeignKeyConstraint(['linked_event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['race_id'], ['race.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event')
    ### end Alembic commands ###
