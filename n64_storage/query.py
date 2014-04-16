
#import sqlalchemy as sql
from sqlalchemy.orm import aliased
from . import models as m

from sqlalchemy import func as f

#from . import parser
from .parser import query_parser

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class TableWrapper(object):
    def __init__(self, cls):
        self.cls = cls

    def __getattr__(self, attr):
        return self.cls.__getattribute__(self.cls, attr)


class EventQuery(object):

    lang_to_column = {
        'id': 'id',
        'info': 'event_info',
        'subtype': 'event_subtype',
        'type': 'event_type',
        'place': 'place',
        'lap': 'lap',
        'player': 'player'
    }


    def __init__(self, query_str, user=None):
        self.query_str = query_str
        self.ident_cache = dict()
        self.alias_cache = dict()
        self.query = None
        self.ordered = False
        self.user = user
        self.parse()
        self.gen_query()


    def parse(self):
        self.parsed = query_parser.parseString(self.query_str)


    def gen_query(self):
        self.query = m.db.session.query()
        self.query = self.query.select_from(m.Event)
        self.query = self.query.join(m.Race)
        self.query = self.query.join(m.Session)
        self.query = self.query.distinct()
        if self.user:
            self.query = self.query.filter(m.Session.owner == self.user)

        # Get a list of all the tables we need to filter by
        for condition in self.parsed[1]:
            if condition[0] != 'not':
                if condition[1] in ['by', 'where']:
                    self.__cache_identifier(condition[2])
                elif condition[1] not in ['with', 'on', 'per']:
                    self.__cache_identifier(condition[3])

        # and the ones we need to output
        for output in self.parsed[0]:
            if output[0] == 'out':
                if output[1][0] not in ['Race', 'Session']:
                    self.__cache_identifier(output[1])
            elif output[0] in ['count', 'average', 'percent', 'out', 'min', 'max']:
                self.__cache_identifier(output[1])
            elif output[0] in ['top', 'bottom']:
                self.__cache_identifier(output[2])

        # generate an alias for each table and join on race_id
        self.__gen_aliases()
        self.__join()
        for f in self.parsed[1]:
            self.__filter(f)
        for o in self.parsed[0]:
            self.__output(o)

        if not self.ordered:
            for item in self.parsed[0]:
                if self.__order(self.parsed[0][0]):
                    break


    def __cache_identifier(self, ident):
        idhash = ''.join(ident.asList())
        self.ident_cache[idhash] = ident.asList()


    def __gen_aliases(self):
        for ident in self.ident_cache.keys():
            if len(self.alias_cache) == 0:
                self.alias_cache[ident] = TableWrapper(m.Event)
            else:
                self.alias_cache[ident] = aliased(m.Event)


    def __join(self):
        base = self.alias_cache.values()[0]
        for table in self.alias_cache.values()[1:]:
            self.query = self.query.join(table, base.race_id==table.race_id)


    def __order(self, output):
        func = output[0]
        out_field = self.lang_to_column[output[-1]]

        if func in ['top', 'bottom']:
            selector = output[2]
        else:
            selector = output[1]

        if selector[0] in ['Session', 'Race']:
            return False

        table = self.alias_cache[''.join(selector)]
        self.query = self.query.order_by(table.__getattr__(out_field))
        return True



    def __find_filter_selector(self, cond):
        if cond[1] in ['per', 'with', 'on']:
            return None
        elif cond[1] in ['by', 'where']:
            return cond[2]
        elif cond[1] in ['more', 'less', 'lap', 'place']:
            return cond[3]
        else:
            return None


    def __filter(self, c):
        bool_op = c[0] == 'not'
        verb = c[1]

        selector = self.__find_filter_selector(c)

        # handle all the simple verbs that don't need a special table
        if verb in ['with', 'on', 'per']:
            if verb == 'with':
                for tab in self.alias_cache.itervalues():
                    self.__with(tab, c[2], bool_op)
            elif verb == 'on':
                self.__on(c[2], bool_op)
            elif verb == 'per':
                self.__per(c[2])
            return

        table = self.alias_cache[''.join(selector)] if selector else None

        if verb == 'by':
            self.__by(table, selector, c[3])
        elif verb == 'less':
            self.__less(table, int(c[2]), selector)
        elif verb == 'more':
            self.__more(table, int(c[2]), selector)
        elif verb == 'place':
            self.__place(table, int(c[2]), selector, bool_op)
        elif verb == 'lap':
            self.__lap(table, int(c[2]), selector, bool_op)
        else:
            self.__default_filter(tab, selector, bool_op)


    def __with(self, tab, char, neg=False):
        if neg:
            self.query = self.query.filter(m.Race.characters[tab.player] != char)
        else:
            self.query = self.query.filter(m.Race.characters[tab.player] == char)


    def __on(self, course, neg=None):
        if neg:
            self.query = self.query.filter(m.Race.course != course)
        else:
            self.query = self.query.filter(m.Race.course == course)


    def __place(self, table, place, selector, neg=False):
        self.query = self.query.filter(table.place == place)
        self.__default_query(table, selector)


    def __lap(self, tab, lap, selector, neg=False):
        self.query = self.query.filter(tab.lap == lap)
        self.__default_query(table, selector)


    def __by(self, table, selector, field):
        column = self.lang_to_column[field]
        self.query = self.query.group_by(table.__getattr__(column))
        self.query = self.query.filter(table.event_subtype == selector[0])
        if len(selector) > 1:
            self.query = self.query.filter(table.event_info == selector[1])


    def __per(self, table, item_type):
        self.query = self.query.filter(
                m.Event.__getattr__(item_type) == table.__getattr__(item_type))


    def __less(self, table, count, selector):
        event = aliased(m.Event)
        if isinstance(TableWrapper, table):
            table = table.cls
        sub = m.db.session.query().select_from(event)\
                .filter(event.race_id == table.race_id)\
                .filter(event.event_subtype == selector[0])\
                .add_column(f.count(event.id).label('ev_count'))\
                .correlate(table)
        if len(selector) > 1:
            sub = sub.filter(event.event_info == selector[1])
        sub = sub.subquery()
        self.query = self.query.filter(sub.as_scalar() < count)


    def __more(self, table, count, selector):
        event = aliased(m.Event)
        if isinstance(table, TableWrapper):
            table = table.cls
        sub = m.db.session.query().select_from(event)\
                .filter(event.race_id == table.race_id)\
                .filter(event.event_subtype == selector[0])\
                .add_column(f.count(event.id).label('ev_count'))\
                .correlate(table)
        if len(selector) > 1:
            sub = sub.filter(event.event_info == selector[1])
        sub = sub.subquery()
        self.query = self.query.filter(sub.as_scalar() > count)


    def __default_filter(self, table, selector, neg=False):
        self.query = self.query.filter(table.event_subtype == selector[0])
        if len(selector) > 1:
            self.query = self.query.filter(table.event_info == selector[1])


    def __output(self, o):
        func = o[0]
        out_field = self.lang_to_column[o[-1]]

        if func in ['top', 'bottom']:
            lim = int(o[1])
            tab = self.alias_cache[''.join(o[2])]
            field = o[-1]
            if func == 'top':
                self.__top(tab, field, lim)
            elif func == 'bottom':
                self.__bottom(tab, field, lim)
            return

        if o[1][0] in ['Race', 'Session']:
            self.__output_other(o[1][0], out_field)
            return

        tab = self.alias_cache[''.join(o[1])]

        if func == 'count':
            self.__count(tab, o[1], out_field)
        elif func == 'average':
            self.__average(tab, o[1], out_field)
        elif func == 'percent':
            self.__percent(tab, o[1], out_field)
        else:
            self.__default_output(tab, o[1], out_field)


    def __top(self, table, field, count):
        self.query = self.query.order_by(table.__getattr__(field))
        self.query = self.query.limit(count)
        self.ordered = True


    def __bottom(self, table, column, field, count):
        self.query = self.query.order_by(table.__getattr__(field).desc())
        self.query = self.query.limit(count)
        self.ordered = True


    def __count(self, table, column, field):
        self.query = self.query.add_columns(f.count(table.__getattr__(field)))
        self.query = self.query.filter(table.event_subtype == column[0])
        if len(column) > 1:
            self.query = self.query.filter(table.event_info == column[1])


    def __min(self, table, column, field):
        self.query = self.query.add_columns(f.min(table.__getattr__(field)))
        self.query = self.query.filter(table.event_subtype == column[0])
        if len(column) > 1:
            self.query = self.query.filter(table.event_info == column[1])


    def __max(self, table, column, field):
        self.query = self.query.add_columns(f.max(table.__getattr__(field)))
        self.query = self.query.filter(table.event_subtype == column[0])
        if len(column) > 1:
            self.query = self.query.filter(table.event_info == column[1])


    def __average(self, table, column, field):
        self.query = self.query.add_columns(f.avg(table.__getattr__(field)))
        self.query = self.query.filter(table.event_subtype == column[0])
        if len(column) > 1:
            self.query = self.query.filter(table.event_info == column[1])


    def __percent(self, table, column, field):
        # this one is hard
        pass


    def __default_output(self, table, column, field):
        self.query = self.query.add_columns(table.__getattr__(field))
        self.query = self.query.filter(table.event_subtype == column[0])

        if len(column) > 1:
            self.query = self.query.filter(table.event_info == column[1])

    def __output_other(self, table, field):
        if table == 'Race':
            self.query = self.query.add_columns(m.Race.__getattribute__(m.Race, field))
        elif table == 'Session':
            self.query = self.query.add_columns(m.Session.__getattribute__(m.Session, field))


