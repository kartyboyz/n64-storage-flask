
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

    def __init__(self, query_str):
        self.query_str = query_str
        self.ident_cache = dict()
        self.alias_cache = dict()
        self.parse()
        self.gen_query()

    def parse(self):
        self.parsed = query_parser.parseString(self.query_str)

    def gen_query(self):
        self.query = m.db.session.query()
        self.query = self.query.select_from(m.Event)
        self.query = self.query.join(m.Race)
        self.query = self.query.join(m.Session)

        # Get a list of all the tables we need to filter by
        for condition in self.parsed[1]:
            self.__cache_identifier(condition[1][1])

        # and the ones we need to output
        for output in self.parsed[0]:
            self.__cache_identifier(output[1])

        # generate an alias for each table and join on race_id
        self.__gen_aliases()
        self.__join()
        self.__filter(self.parsed[1])
        for o in self.parsed[0]:
            self.__output(o)

    def __cache_identifier(self, ident):
        print ident
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


    def __filter(self, cond):
        for c in cond:
            #bool_op = c[0]
            rest = c[1]
            verb = rest[0]

            if verb in ['with', 'on']:
                if verb == 'with':
                    self.query = self.query.filter(m.Race.characters[m.Event.player] == rest[1])
                elif verb == 'on':
                    self.query = self.query.filter(m.Race.course == rest[1])
                else:
                    return

            sel = rest[1]
            col = self.lang_to_column[sel[-1]]
            tab = self.alias_cache[''.join(sel)]
            print tab

            if verb == 'by':
                print "self.query.group_by(tab.__getattr__(%s))" % col
                self.query = self.query.group_by(tab.__getattr__(col))
            elif verb == 'per':
                pass
            elif verb == 'less':
                pass
            elif verb == 'more':
                pass
            else:
                print "self.query.filter(tab.event_info == %s)" % col
                self.query = self.query.filter(tab.event_info == sel[-1])

    def __output(self, o):
        func = o[0]
        what = self.lang_to_column[o[-1]]

        if func in ['top', 'bottom']:
            lim = int(o[1])
            self.query = self.query.limit(lim)
            self.query = self.query.order_by()

        tab = self.alias_cache[''.join(o[1])]
        print tab
        #sel = o[-1]

        if func == 'count':
            print "self.query.add_columns(f.count(tab.__getattr__(%s)))" % what
            self.query = self.query.add_columns(f.count(tab.__getattr__(what)))
        elif func == 'average':
            pass
        elif func == 'percent':
            pass
        else: # out
            print "self.query.add_columns(tab.__getattr__(%s))" % what
            self.query = self.query.add_columns(tab.__getattr__(what))
