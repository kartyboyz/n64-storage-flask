import pyparsing
from .. import parser as p
#from .. import query as q
import unittest


class ParserTestCase(unittest.TestCase):

    def _do_parse_test(self, spec, good=list(), bad=list()):
        for t in good:
            self.assertIsNotNone(spec.parseString(t))
        for t in bad:
            with self.assertRaises(pyparsing.ParseException):
                spec.parseString(t, True)

    def test_subtype_spec(self):
        good = [
            'Lap.3',
            'Finish.4',
            'Watch',
            'Get.red',
            'Use.blue',
            'Passing.3',
            'Passed.2',
            'Shortcut',
        ]
        bad = [
            'L',
            'asdfasdf',
            'Lap.3, meow'
        ]
        self._do_parse_test(p.subtype_spec, good, bad)

    def test_field_spec(self):
        good = [
            'percent Lap.3 info',
            'count Use',
            'average Get lap',
            'count Shortcut',
            'count Passing.1',
            'top 5 Use',
            'bottom 19 Get.lightning',
            'Lap.Lap',
            'Pass.passing'
        ]
        bad = [
            'prcnt asf meow',
            'percent Lap.3 aaa',
            'top -5 Use',
            'asdfasdf'
        ]
        self._do_parse_test(p.field_spec, good, bad)

    def test_condition_statement(self):
        good = [
            'on KoopaTroopaBeach',
            'and with Bowser',
            'by Finish',
            'not shortcut',
            'more than 5 item.get'
        ]
        bad = [
            'asdfasdf',
            'by player',
            'more than 5 lap.lap.lap.lap'
        ]
        self._do_parse_test(p.neg_cond_spec, good, bad)

    def test_condition_list(self):
        good = [
            'by Finish, not lap 3 shortcut',
            'by Finish, on KoopaTroopaBeach',
            'by Finish, more than 6 Item'
        ]
        bad = [
            'by place, (not shortcut'
            'adsf',
            'place'
        ]
        self._do_parse_test(p.condition_statement, good, bad)


        
    
