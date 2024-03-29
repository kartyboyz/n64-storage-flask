"""add missing columns

Revision ID: 20c9101ad47f
Revises: 320e59eac25d
Create Date: 2014-04-09 21:29:35.775367

"""

# revision identifiers, used by Alembic.
revision = '20c9101ad47f'
down_revision = '320e59eac25d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('place', sa.Integer(), nullable=True))
    op.add_column('race', sa.Column('audio_processed', sa.Boolean(), nullable=True))
    op.add_column('race', sa.Column('audio_url', sa.VARCHAR(length=1024), nullable=True))
    op.add_column('race', sa.Column('video_processed_url', sa.VARCHAR(length=1024), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('race', 'video_processed_url')
    op.drop_column('race', 'audio_url')
    op.drop_column('race', 'audio_processed')
    op.drop_column('event', 'place')
    ### end Alembic commands ###
