
#import sqlalchemy as sql
from sqlalchemy.orm import aliased
from sqlalchemy import cast

from collections import OrderedDict

from sqlalchemy import func as f

from . import models as m
from . import parser
from .parser import query_parser

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class TableWrapper(object):
    def __init__(self, cls):
        self.cls = cls

    def __getattr__(self, attr):
        return self.cls.__getattribute__(self.cls, attr)


class LanguageDescription(object):

    def __init__(self):
        self.fields = parser.event_fields
        self.event_types = parser.event_types + parser.event_subtypes
        self.selectors = {t:self.__get_event_infos(t) for t in self.event_types}

        # clear out empty selectors
        for inf in self.selectors.keys():
            if len(self.selectors[inf]) == 0:
                del self.selectors[inf]

        self.selectors['Time'] = []

        self.players = parser.players
        self.courses = parser.courses
        self.selector = ['types', 'infos']
        self.outputs = {
            'count':  ['selector', 'field'],
            'average': ['selector', 'field'],
            'min': ['selector', 'field'],
            'max': ['selector', 'field'],
            #'top': ['int', 'selector', '?field'],
            #'bottom': ['int', 'selector', '?field'],
            'out': ['selector', 'field']
        }
        self.filters = {
            'on': ['courses'],
            'with': ['characters'],
            'by': ['selector', 'field'],
            'less': ['int', 'selector'],
            'more': ['int', 'selector'],
            'lap': ['int', 'selector'],
            'place': ['int', 'selector'],
            'where': ['selector']
        }

    def __get_event_infos(self, et):
        q = m.db.session.query()\
                .select_from(m.Event)\
                .add_columns(m.Event.event_info)\
                .order_by(m.Event.event_info)\
                .distinct()
        q = q.filter((cast(m.Event.event_type, m.db.String) == et)
                | (m.Event.event_subtype == et))

        return [i[0] for i in q.all() if len(i[0]) > 0]

    def to_dict(self):
        d = {
            'outputs': self.outputs,
            'filters': self.filters,

            'selectors': self.selectors,

            'fields': self.fields,
            'characters': self.players,
            'courses': self.courses,
        }
        return d


class EventQuery(object):

    lang_to_column = {
        'id': 'id',
        'race' : 'race_id',
        'session': 'session_id',
        'info': 'event_info',
        'subtype': 'event_subtype',
        'type': 'event_type',
        'place': 'place',
        'lap': 'lap',
        'player': 'player',
        'course': 'course',
        'time': 'timestamp',
    }


    def __init__(self, query_str, user=None):
        self.query_str = query_str
        self.ident_cache = list()
        self.alias_cache = OrderedDict()
        self.after_query = list()
        self.column_names = list()
        self.column_types = list()
        self.query = None
        self.ordered = False
        self.user = user
        self.parse()
        self.gen_query()


    def parse(self):
        self.parsed = query_parser.parseString(self.query_str)


    def gen_query(self):

        # Get a list of all the tables we need to filter by
        if len(self.parsed) > 1:
            for condition in self.parsed[1]:
                if condition[1] in ['by', 'where']:
                    if condition[2][0] not in ['Session', 'Race']:
                        self.__cache_identifier(condition[2])
                elif condition[1] not in ['with', 'on', 'per']:
                    if condition[3][0] not in ['Session', 'Race']:
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

        self.alias_cache['Race'] = TableWrapper(m.Race)
        self.alias_cache['Session'] = TableWrapper(m.Session)

        table = self.alias_cache.values()[0]

        self.query = m.db.session.query()
        self.query = self.query.select_from(table)
        self.query = self.query.join(m.Race, table.race_id==m.Race.id)
        self.query = self.query.join(m.Session)
        self.query = self.query.distinct()

        if self.user:
            self.query = self.query.filter(m.Session.owner == self.user)

        self.__join()


        if len(self.parsed) > 1:
            for fi in self.parsed[1]:
                self.__filter(fi)
        for o in self.parsed[0]:
            self.__output(o)

        for fn in self.after_query: self.query = fn()

        if not self.ordered and len(self.parsed[0]) > 1:
            for item in self.parsed[0]:
                if self.__order(self.parsed[0][0]):
                    break


    def __cache_identifier(self, ident):
        idhash = ''.join(ident.asList())
        self.ident_cache.append(idhash)


    def __gen_aliases(self):
        for ident in self.ident_cache:
            if ident == 'Time':
                self.alias_cache[ident] = aliased(m.LaptimeEvent)
            else:
                self.alias_cache[ident] = aliased(m.Event)


    def __join(self):
        if len(self.alias_cache.values()) > 2:
            base = self.alias_cache.values()[0]
            for table in self.alias_cache.values()[1:-2]:
                self.query = self.query.join(table, base.race_id==table.race_id)


    def __order(self, output):
        func = output[0]
        out_field = self.lang_to_column[output[-1]]

        if func in ['top', 'bottom']:
            selector = output[2]
        else:
            selector = output[1]

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
                for key, table in self.alias_cache.iteritems():
                    if key not in ['Race', 'Session']:
                        self.__with(table, c[2], bool_op)
            elif verb == 'on':
                self.__on(c[2], bool_op)
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
            self.__default_filter(table, selector, bool_op)


    def __with(self, table, char, neg=False):
        if neg:
            self.query = self.query.filter(m.Race.characters[table.player] != char)
        else:
            self.query = self.query.filter(m.Race.characters[table.player] == char)


    def __on(self, course, neg=None):
        if neg:
            self.query = self.query.filter(m.Race.course != course)
        else:
            self.query = self.query.filter(m.Race.course == course)


    def __place(self, table, place, selector, neg=False):
        if not neg:
            self.query = self.query.filter(table.place == place)
            self.__default_filter(table, selector, neg)
        else:
            sub, e = self.__count_query(table, selector)
            sub = sub.filter(e.place == place)
            self.query = self.query.filter(sub.subquery().as_scalar() == 0)


    def __lap(self, table, lap, selector, neg=False):
        if not neg:
            self.query = self.query.filter(table.lap == lap)
            self.__default_filter(table, selector, neg)
        else:
            sub, e = self.__count_query(table, selector)
            sub = sub.filter(e.lap == lap)
            self.query = self.query.filter(sub.subquery().as_scalar() == 0)


    def __by(self, table, selector, field):
        column = self.lang_to_column[field]
        self.query = self.query.group_by(table.__getattr__(column))
        self.query = self.__match_selector(self.query, table, selector)


    def __less(self, table, count, selector):
        sub, e = self.__count_query(table, selector)
        self.query = self.query.filter(sub.subquery().as_scalar() < count)


    def __more(self, table, count, selector):
        sub, e = self.__count_query(table, selector)
        self.query = self.query.filter(sub.subquery().as_scalar() > count)


    def __count_query(self, table, selector):
        event = aliased(m.Event)
        sub = m.db.session.query().select_from(event)\
                .filter(event.race_id == table.race_id)\
                .add_column(f.count(event.id).label('ev_count'))\
                .correlate(table)
        sub = self.__match_selector(sub, event, selector)
        return sub, event


    def __default_filter(self, table, selector, neg=False):
        if not neg:
            self.query = self.__match_selector(self.query, table, selector)
        else:
            sub, e = self.__count_query(table, selector)
            self.query = self.query.filter(sub.subquery().as_scalar() == 0)


    def __match_selector(self, query, table, selector):
        q = query
        try:
            if selector[0] in parser.event_subtypes:
                q = q.filter(table.event_subtype == selector[0])
            else:
                q = q.filter(table.event_type == selector[0])

            if len(selector) > 1:
                q = q.filter(table.event_info == selector[1])

            return q
        except AttributeError:
            return q


    def __output(self, o):
        func = o[0]
        out_field = self.lang_to_column[o[-1]]

        if func in ['top', 'bottom']:
            lim = int(o[1])
            col = o[2]
            table = self.alias_cache[''.join(col)]
            if func == 'top':
                self.__top(lim, table, col, out_field)
            elif func == 'bottom':
                self.__bottom(lim, table, col, out_field)
            return

        table = self.alias_cache[''.join(o[1])]

        if func == 'count':
            self.__count(table, o[1], out_field)
        elif func == 'average':
            self.__average(table, o[1], out_field)
        elif func == 'min':
            self.__min(table, o[1], out_field)
        elif func == 'max':
            self.__max(table, o[1], out_field)
        else:
            self.__default_output(table, o[1], out_field)


    def __top(self, count, table, column, field):
        self.query = self.query.order_by(table.__getattr__(field).desc())
        self.after_query.append(lambda:self.query.limit(count))
        self.ordered = True
        self.__default_output(table, column, field)


    def __bottom(self, count, table, column, field):
        self.query = self.query.order_by(table.__getattr__(field))
        self.after_query.append(lambda:self.query.limit(count))
        self.ordered = True
        self.__default_output(table, column, field)


    def __count(self, table, column, field):
        self.query = self.query.add_columns(f.count(table.__getattr__(field)))
        self.__default_filter(table, column)


    def __min(self, table, column, field):
        self.query = self.query.add_columns(f.min(table.__getattr__(field)))
        self.__default_filter(table, column)


    def __max(self, table, column, field):
        self.query = self.query.add_columns(f.max(table.__getattr__(field)))
        self.__default_filter(table, column)


    def __average(self, table, column, field):
        self.query = self.query.add_columns(f.avg(table.__getattr__(field)))
        self.__default_filter(table, column)


    def __default_output(self, table, column, field):
        self.query = self.query.add_columns(table.__getattr__(field))
        self.__default_filter(table, column)


