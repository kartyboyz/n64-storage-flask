import pyparsing
from .. import parser as p
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


class QueryTestCase(unittest.TestCase):

    def test_output_simple(self):
        qe = q.EventQuery("Shortcut")
        al = qe.query.all()
        self.assertIsNotNone(al)
        self.assertEqual(len(al[0]), 1)


    def test_output_field(self):
        for field in ['place', 'lap', 'player', 'event_subtype', 'event_type', 'time']:
            qe = q.EventQuery("Shortcut %s" % field)
            al = qe.query.all()
            self.assertIsNotNone(al)
            self.assertEqual(len(al[0]), 1)


    def test_output_race(self):
        qe = q.EventQuery("Race course")
        al = qe.query.all()
        for item in al:
            if item[0] != '':
                self.assertIn(item[0].replace(" ", ""), p.courses)


    def test_output_multiple(self):
        qe = q.EventQuery("Item, Finish")
        al = qe.query.all()
        self.assertIsNotNone(al)
        self.assertEqual(len(al[0]), 2)


    def test_output_limit(self):
        qe = q.EventQuery("top 5 Item id")
        al = qe.query.all()
        self.assertLessEqual(len(al), 5)
        qe = q.EventQuery("bottom 2 Item id")
        al = qe.query.all()
        self.assertLessEqual(len(al), 2)


    def test_output_count(self):
        qe = q.EventQuery("count Item")
        al = qe.query.all()
        self.assertGreater(al[0][0], 100)


    def test_output_average(self):
        qe = q.EventQuery("average Item place: place 2 Item")
        al = qe.query.all()
        self.assertEqual(int(al[0][0]), 2)


    def test_output_min(self):
        qe = q.EventQuery("min Item place")
        al = qe.query.all()
        self.assertEqual(al[0][0], 1)


    def test_output_max(self):
        qe = q.EventQuery("max Item place")
        al = qe.query.all()
        self.assertEqual(al[0][0], 4)


    def test_filter(self):
        qe = q.EventQuery("Item type, Item subtype: Item")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertEqual(item[0], 'Item')
            self.assertIn(item[1], ['Get', 'Use', 'Box', 'Steal', 'Stolen'])


    def test_filter_on(self):
        qe = q.EventQuery("Race course: on KoopaTroopaBeach")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertEquals(item[0], 'KoopaTroopaBeach')
        qe = q.EventQuery("Race course: not on KoopaTroopaBeach")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertNotEquals(item[0], 'KoopaTroopaBeach')


    def test_filter_by(self):
        qe = q.EventQuery("Finish: by Finish")
        al = qe.query.all()
        self.assertIsNotNone(al)
        self.assertEqual(len(al[0]), 1)


    def test_filter_with(self):
        qe = q.EventQuery("Item player: with Toad")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertEqual(item[0], "Toad")
        qe = q.EventQuery("Item player: not with Toad")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertNotEqual(item[0], "Toad")


    def test_filter_less_than(self):
        qe = q.EventQuery("count Item: less than 30 Item, by Race id")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertLess(item[0], 30)


    def test_filter_more_than(self):
        qe = q.EventQuery("count Item: more than 30 Item, by Race id")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertGreater(item[0], 30)


    def test_filter_place(self):
        qe = q.EventQuery("Item place: place 2 Item")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertEqual(al[0][0], 2)
        qe = q.EventQuery("Shortcut place: not place 2 Shortcut")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertNotEqual(al[0][0], 2)


    def test_filter_lap(self):
        qe = q.EventQuery("Item lap: lap 3 Item")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertEqual(al[0][0], 3)
        qe = q.EventQuery("Item lap: not lap 3 Shortcut")
        al = qe.query.all()
        self.assertIsNotNone(al)
        for item in al:
            self.assertNotEqual(al[0][0], 3)

