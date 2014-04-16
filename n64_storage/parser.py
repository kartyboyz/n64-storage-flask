
from pyparsing import oneOf, Word, Suppress
from pyparsing import CaselessKeyword
from pyparsing import Forward, Group, delimitedList, Optional
from pyparsing import alphanums, nums

event_types = ['Lap', 'Item', 'Collision', 'Pass', 'Shortcut', 'Tag', 'Fall', 'Reverse']
event_subtypes = ['Race', 'Session', 'Get', 'Use', 'Steal', 'Stolen', 'Passing', 'Passed', 'Start', 'Lap', 'Finish', 'Shortcut', 'Watch', 'Tag', 'Banana', 'Spin', 'Crash']
event_fields = ['id', 'lap', 'info', 'subtype', 'type', 'place', 'player']
race_fields = ['course', 'characters']

booleans = ['and', 'not']
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


field_spec = Optional(oneOf(event_fields), default='info')

count_spec = CaselessKeyword('count') + subtype_spec + field_spec
average_spec = CaselessKeyword('average') + subtype_spec + field_spec
percent_spec = CaselessKeyword('percent') + subtype_spec + field_spec
min_spec = CaselessKeyword('min') + subtype_spec + field_spec
max_spec = CaselessKeyword('max') + subtype_spec + field_spec
top_spec = CaselessKeyword('top') + Word(nums) + subtype_spec + field_spec
bottom_spec = CaselessKeyword('bottom') + Word(nums) + subtype_spec + field_spec
default_spec = Optional(CaselessKeyword('out'), default="out") + subtype_spec + field_spec

select_spec = Group(count_spec | average_spec | percent_spec | top_spec | bottom_spec |
        min_spec | max_spec | default_spec)
selection_statement = delimitedList(select_spec)


boolean_spec = CaselessKeyword(booleans[0])
for b in booleans[1:]:
    boolean_spec |= CaselessKeyword(b)

on_spec = CaselessKeyword('on') + oneOf(courses, caseless=True)
with_spec = CaselessKeyword('with') + oneOf(players, caseless=True)
per_spec = CaselessKeyword('per') + oneOf(['lap', 'race'], caseless=True)
by_spec = CaselessKeyword('by') + subtype_spec + field_spec
less_spec = CaselessKeyword('less') + Suppress('than') + Word(nums) + subtype_spec + field_spec
more_spec = CaselessKeyword('more') + Suppress('than') + Word(nums) + subtype_spec + field_spec
lap_spec = CaselessKeyword('lap') + Word(nums) + subtype_spec
place_spec = CaselessKeyword('place') + Word(nums) + subtype_spec

default_cond_spec = Optional(CaselessKeyword('where'), default='where') + subtype_spec


#condition_statement = Forward()

cond_spec = on_spec | with_spec | by_spec | per_spec | less_spec | more_spec \
        | lap_spec | place_spec | default_cond_spec

neg_cond_spec = Group(Optional(boolean_spec, default='and') + cond_spec)

condition_statement = delimitedList(neg_cond_spec)

query_spec = Group(selection_statement) + Suppress(':') + Group(condition_statement)

query_parser = query_spec
