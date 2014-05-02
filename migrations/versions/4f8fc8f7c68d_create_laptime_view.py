"""create laptime view

Revision ID: 4f8fc8f7c68d
Revises: 4d73c542db51
Create Date: 2014-05-01 21:45:38.669382

"""

# revision identifiers, used by Alembic.
revision = '4f8fc8f7c68d'
down_revision = '4d73c542db51'

from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import literal_column, cast, select
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table
from sqlalchemy.orm import Query

from n64_storage import models
from n64_storage.models import db

event = models.Event.metadata.tables['event']


class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable


class DropView(DDLElement):
    def __init__(self, name):
        self.name = name


@compiles(CreateView)
def compile_create_view(element, compiler, **kw):
    import ipdb
    ipdb.set_trace()
    return "CREATE VIEW %s AS %s" % (element.name, compiler.sql_compiler.process(element.selectable))


@compiles(DropView)
def compile_drop_view(element, compiler, **kw):
    return "DROP VIEW IF EXISTS %s" % (element.name)


def View(name, selectable):
    """
        `View` support for SQLAlchemy
        See: http://www.sqlalchemy.org/trac/wiki/UsageRecipes/Views
    """

    t = table(name)

    if isinstance(selectable, Query):
        selectable = selectable.subquery()

    for c in selectable.c:
        c._make_proxy(t)

    CreateView(name, selectable).execute_at('after-create', db.metadata)
    DropView(name).execute_at('before-drop', db.metadata)

    return t



def upgrade():
    e = event.alias()
    e1 = event.alias()
    create_laptime_view = CreateView("laptime",
            select([e.c.id.label('id'),
                e.c.race_id.label('race_id'),
                e.c.player.label('player'),
                e.c.timestamp.label('timestamp'),
                (e.c.lap - 1).label('lap'),
                e.c.place.label('place'),
                e.c.event_number.label('event_number'),
                e.c.event_type.label('event_type'),
                literal_column("Time").label('event_subtype'),
                cast(e.c.timestamp - e1.c.timestamp, db.String).label('event_info'),
                e.c.linked_event_id.label('linked_event_id'),
                e.c.image_url.label('image_url')]).\
            select_from(e.join(e1, e1.c.race_id == e.c.race_id)).\
            where((e.c.event_type == "Lap")
                & (e.c.event_subtype == "New")
                & (e1.c.event_type == "Lap")
                & (e1.c.event_subtype == "New")
                & (e1.c.player == e.c.player)
                & (cast(e.c.event_info, db.Integer) == (cast(e1.c.event_info, db.Integer) + 1))))
    op.execute(create_laptime_view)


def downgrade():
    drop_laptime_view = DropView('laptime')
    op.execute(drop_laptime_view)

