import pyparsing
from .. import query as q
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
        self._do_parse_test(q.subtype_spec, good, bad)

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
        self._do_parse_test(q.field_spec, good, bad)

    def test_condition_statement(self):
        good = [
            'or on KoopaTroopaBeach',
            'and with Bowser',
            'by place',
            'not shortcut',
            'more than 5 item.get'
        ]
        bad = [
            'or not on KoopaTroopaBeach',
            'and with KingBoo',
            'by time',
            'more than 5 lap.lap.lap.lap'
        ]
        self._do_parse_test(q.neg_cond_spec, good, bad)

    def test_condition_list(self):
        good = [
            'by place, (not shortcut, lap.3)',
            'by place,not (shortcut, lap.3)',
            'by place, (shortcut, (not lap.3))'
        ]
        bad = [
            'by place, (not shortcut'
            'adsf',
            'place'
        ]
        self._do_parse_test(q.condition_statement, good, bad)

    def test_query(self):
        pass
