
#import sqlalchemy as sql
from sqlalchemy.orm import aliased
from . import models as m

#from . import parser
from .parser import query_parser


class EventQuery(object):
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
            self.__cache_identifier(output[0][1])

        # generate an alias for each table and join on race_id
        self.__gen_aliases()
        self.__join()

    def __cache_identifier(self, ident):
        idhash = ''.join(ident.asList())
        self.ident_cache[idhash] = ident.asList()

    def __gen_aliases(self):
        for ident in self.ident_cache.keys():
            if len(self.alias_cache) == 0:
                self.alias_cache[ident] = m.Event
            else:
                self.alias_cache[ident] = aliased(m.Event)

    def __join(self):
        base = self.alias_cache.values()[0]
        for table in self.alias_cache.values()[1:]:
            self.query = self.query.join(table, base.race_id==table.race_id)

