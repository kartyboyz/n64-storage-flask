
import sys, pyparsing
from pyparsing import oneOf, Word, Literal, Suppress, ZeroOrMore, Keyword
from pyparsing import CaselessKeyword, CaselessLiteral
from pyparsing import ParseException, Forward, Group, delimitedList, Optional
from pyparsing import alphanums, alphas, nums

import sqlalchemy as sql
from . import models as m

event_types = ['Lap', 'Item', 'Collision', 'Pass', 'Shortcut', 'Tag']
event_subtypes = ['Get', 'Use', 'Passing', 'Passed', 'Start', 'Lap', 'Finish', 'Shortcut', 'Watch', 'Tag', 'Banana', 'Spin', 'Crash']
event_fields = ['id', 'lap', 'info', 'subtype', 'type', 'place', 'player']
race_fields = ['course', 'characters']

booleans = ['and', 'or', 'not']
conditions = ['on', 'by', 'with']

players = ['Yoshi', 'Toad', 'Peach', 'Bowser', 'Mario', 'Luigi', 'Bowser', 'DonkeyKong']
items = ['Banana', 'BananaBunch', 'Boo', 'FakeItemBox', 'GreenShell', 'TripleGreenShells',
         'RedShell', 'TripleRedShells', 'BlueSpinyShell', 'Mushroom', 'TripleMushrooms',
         'GoldenMushroom', 'Star', 'Thunderbolt']

courses = ['LuigiCircuit', 'MooMooFarm', 'KoopaTroopaBeach', 'KalimariDesert', 'ToadsTurnpike',
           'FrappeSnowland', 'ChocoMountain', 'MarioRaceway', 'WarioStadium', 'SherbertLand',
           'RoyalRaceway', 'BowsersCastle', 'DKsJungleParkway', 'BansheeBoardwalk', 'RainbowRoad']



event_type_spec = oneOf(event_types, caseless=True)
event_subtype_spec = oneOf(event_subtypes, caseless=True)
info_spec = Word(alphanums)

subtype_spec = Group(event_subtype_spec + Optional(Suppress('.') + info_spec))
event_spec = Group(event_type_spec + Suppress('.') + Optional(subtype_spec))


field_spec = Optional(oneOf(event_fields), default='id')

count_spec = Group(CaselessKeyword('count') + subtype_spec) + field_spec
average_spec = Group(CaselessKeyword('average') + subtype_spec) + field_spec
percent_spec = Group(CaselessKeyword('percent') + subtype_spec) + field_spec
top_spec = Group(CaselessKeyword('top') + Word(nums) + subtype_spec) + field_spec
bottom_spec = Group(CaselessKeyword('bottom') + Word(nums) + subtype_spec) + field_spec
default_spec = Optional(event_spec) + field_spec

select_spec = Group(count_spec | average_spec | percent_spec | top_spec | bottom_spec | default_spec)
selection_statement = delimitedList(select_spec)


boolean_spec = CaselessKeyword(booleans[0])
for b in booleans[1:]:
    boolean_spec |= CaselessKeyword(b)

on_spec = Group(CaselessKeyword('on') + oneOf(courses, caseless=True))
with_spec = Group(CaselessKeyword('with') + oneOf(players, caseless=True))
per_spec = Group(CaselessKeyword('per') + oneOf(['lap', 'race'], caseless=True))
by_spec = Group(CaselessKeyword('by') + field_spec)
default_cond_spec = subtype_spec
less_spec = Group(CaselessKeyword('less') + Suppress('than') + Word(nums) + default_spec)
more_spec = Group(CaselessKeyword('more') + Suppress('than') + Word(nums) + default_spec)


condition_statement = Forward()

cond_spec = on_spec | with_spec | by_spec | per_spec | less_spec | more_spec | default_cond_spec | (Suppress('(') + condition_statement + Suppress(')'))
neg_cond_spec = Group(Optional(boolean_spec, default='and') + cond_spec)

condition_statement << delimitedList(neg_cond_spec)


query_spec = Group(selection_statement) + Suppress(':') + Group(condition_statement)

query_parser = query_spec

class EventQuery(object):
    def __init__(self, query_str):
        self.query_str = query_str
        self.parse()
        self.gen_query()
        self.ident_cache = dict()
        self.alias_cache = dict()

    def parse(self):
        self.parsed = query_parser.parseString(self.query_str)

    def gen_query(self):
        self.query = m.db.session.query(m.Event)
        self.query = self.query.join(m.Race)

        for output in self.parsed[0]:
            self.append_output(output)

        for condition in self.parsed[1]:
            self.append_condition(condition)

    def identifier(self, ident):
        pass

    def append_output(self, output):
        pass
