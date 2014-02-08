"""lengthen video_url column

Revision ID: 3084fad1915e
Revises: 34133c318c56
Create Date: 2014-02-08 16:05:18.073761

"""

# revision identifiers, used by Alembic.
revision = '3084fad1915e'
down_revision = '34133c318c56'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('session', 'video_url', type_=sa.VARCHAR(length=1024),
            existing_type=sa.VARCHAR(length=100))
    op.alter_column('race', 'video_url', type_=sa.VARCHAR(length=1024),
            existing_type=sa.VARCHAR(length=100))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('session', 'video_url', type_=sa.VARCHAR(length=100),
            existing_type=sa.VARCHAR(length=1024))
    op.alter_column('race', 'video_url', type_=sa.VARCHAR(length=100),
            existing_type=sa.VARCHAR(length=1024))
    ### end Alembic commands ###

