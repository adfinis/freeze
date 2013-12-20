import jedi.parser as parser
import pympler.asizeof as size
try:
    import unittest2            as unittest
except ImportError:  # pragma: no cover
    import unittest

import freeze


class JediTest(unittest.TestCase):
    def test_freeze_with_jedi(self):
        source = open("lib/freeze.py", "r").read()
        prs = parser.Parser(source)
        a = freeze.dump(prs)
        b = freeze.freeze(a)
        c = freeze.recursive_sort(b)
        self.assertGreater(len(a), 0)
        self.assertGreater(len(b), 0)
        self.assertGreater(len(c), 0)
        self.assertGreater(size.asizeof(b), 2038400)
